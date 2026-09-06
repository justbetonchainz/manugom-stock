from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from inventory.models import MouvementStock, Pneu
from inventory.services import ServiceStock

from .models import Commande, LigneCommande, Panier


ALLOWED_TRANSITIONS = {
    Commande.Statut.PENDING: {Commande.Statut.CONFIRMED, Commande.Statut.CANCELLED},
    Commande.Statut.CONFIRMED: {Commande.Statut.PREPARING, Commande.Statut.CANCELLED},
    Commande.Statut.PREPARING: {Commande.Statut.READY},
    Commande.Statut.READY: {Commande.Statut.SHIPPED, Commande.Statut.DELIVERED},
    Commande.Statut.SHIPPED: {Commande.Statut.DELIVERED},
    Commande.Statut.DELIVERED: set(),
    Commande.Statut.CANCELLED: set(),
}


class ServiceCommande:
    @staticmethod
    @transaction.atomic
    def creer_depuis_panier(*, panier, adresse, ville, type_reception, mode_paiement, notes=""):
        panier = Panier.objects.select_for_update().select_related("client").get(pk=panier.pk, actif=True)
        lignes = list(panier.lignes.select_related("pneu", "pneu__marque"))
        if not lignes:
            raise ValidationError("Le panier est vide.")
        pneus = {p.pk: p for p in Pneu.objects.select_for_update().filter(pk__in=[l.pneu_id for l in lignes])}
        for ligne in lignes:
            pneu = pneus[ligne.pneu_id]
            if pneu.statut != Pneu.Statut.ACTIVE:
                raise ValidationError(f"La référence {pneu.reference_interne} est inactive.")
            if ligne.quantite > pneu.quantite_disponible:
                raise ValidationError(f"Stock insuffisant pour {pneu.reference_interne}.")
        commande = Commande.objects.create(
            client=panier.client,
            adresse=adresse,
            ville=ville,
            type_reception=type_reception,
            mode_paiement=mode_paiement,
            notes=notes,
        )
        total = Decimal("0")
        for ligne in lignes:
            pneu = pneus[ligne.pneu_id]
            sous_total = pneu.prix_vente * ligne.quantite
            LigneCommande.objects.create(
                commande=commande,
                pneu=pneu,
                reference_pneu=pneu.reference_interne,
                marque=pneu.marque.nom,
                modele=pneu.modele,
                dimension=pneu.dimension_complete,
                quantite=ligne.quantite,
                prix_unitaire=pneu.prix_vente,
                sous_total=sous_total,
            )
            total += sous_total
        commande.montant_total = total
        commande.save(update_fields=["montant_total", "date_modification"])
        panier.actif = False
        panier.save(update_fields=["actif", "date_modification"])
        return commande

    @staticmethod
    @transaction.atomic
    def confirmer(*, commande, utilisateur):
        commande = Commande.objects.select_for_update().get(pk=commande.pk)
        if commande.statut != Commande.Statut.PENDING or commande.stock_retire:
            raise ValidationError("Cette commande ne peut pas être confirmée une seconde fois.")
        lignes = list(commande.lignes.select_related("pneu"))
        pneus = {p.pk: p for p in Pneu.objects.select_for_update().filter(pk__in=[l.pneu_id for l in lignes])}
        for ligne in lignes:
            pneu = pneus[ligne.pneu_id]
            if pneu.statut != Pneu.Statut.ACTIVE or pneu.quantite_disponible < ligne.quantite:
                raise ValidationError(f"Stock insuffisant ou référence inactive : {ligne.reference_pneu}.")
        for ligne in lignes:
            ServiceStock.appliquer_mouvement(
                pneu=pneus[ligne.pneu_id],
                quantite=ligne.quantite,
                type_mouvement=MouvementStock.Type.EXIT,
                motif=f"Confirmation de la commande {commande.numero}",
                utilisateur=utilisateur,
                commande=commande,
            )
        commande.statut = Commande.Statut.CONFIRMED
        commande.stock_retire = True
        commande.save(update_fields=["statut", "stock_retire", "date_modification"])
        return commande

    @staticmethod
    @transaction.atomic
    def annuler(*, commande, utilisateur):
        commande = Commande.objects.select_for_update().get(pk=commande.pk)
        if commande.statut not in {Commande.Statut.PENDING, Commande.Statut.CONFIRMED}:
            raise ValidationError("L'annulation n'est plus autorisée à cette étape.")
        if commande.stock_retire:
            if commande.stock_restaure:
                raise ValidationError("Le stock a déjà été restauré.")
            for ligne in commande.lignes.select_related("pneu"):
                ServiceStock.appliquer_mouvement(
                    pneu=ligne.pneu,
                    quantite=ligne.quantite,
                    type_mouvement=MouvementStock.Type.RETURN,
                    motif=f"Annulation de la commande {commande.numero}",
                    utilisateur=utilisateur,
                    commande=commande,
                )
            commande.stock_restaure = True
        commande.statut = Commande.Statut.CANCELLED
        commande.save(update_fields=["statut", "stock_restaure", "date_modification"])
        return commande

    @staticmethod
    @transaction.atomic
    def changer_statut(*, commande, nouveau_statut, utilisateur):
        if nouveau_statut == Commande.Statut.CONFIRMED:
            return ServiceCommande.confirmer(commande=commande, utilisateur=utilisateur)
        if nouveau_statut == Commande.Statut.CANCELLED:
            return ServiceCommande.annuler(commande=commande, utilisateur=utilisateur)
        commande = Commande.objects.select_for_update().get(pk=commande.pk)
        if nouveau_statut not in ALLOWED_TRANSITIONS.get(commande.statut, set()):
            raise ValidationError("Transition de statut non autorisée.")
        if nouveau_statut == Commande.Statut.SHIPPED and commande.type_reception != Commande.Reception.DELIVERY:
            raise ValidationError("Une commande en retrait ne peut pas être expédiée.")
        if nouveau_statut == Commande.Statut.DELIVERED and commande.statut == Commande.Statut.READY and commande.type_reception != Commande.Reception.PICKUP:
            raise ValidationError("Une livraison doit d'abord être expédiée.")
        commande.statut = nouveau_statut
        commande.save(update_fields=["statut", "date_modification"])
        return commande

