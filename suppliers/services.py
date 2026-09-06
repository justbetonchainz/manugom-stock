from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from inventory.models import MouvementStock, Pneu
from inventory.services import ServiceStock

from .models import Approvisionnement


class ServiceApprovisionnement:
    @staticmethod
    @transaction.atomic
    def receptionner(*, approvisionnement, utilisateur):
        approvisionnement = Approvisionnement.objects.select_for_update().get(pk=approvisionnement.pk)
        if approvisionnement.statut == Approvisionnement.Statut.RECEIVED or approvisionnement.recu_le:
            raise ValidationError("Cet approvisionnement a déjà été reçu.")
        if approvisionnement.statut != Approvisionnement.Statut.ORDERED:
            raise ValidationError("Seul un approvisionnement commandé peut être reçu.")
        lignes = list(approvisionnement.lignes.select_related("pneu"))
        if not lignes:
            raise ValidationError("L'approvisionnement ne contient aucune ligne.")
        pneus = {p.pk: p for p in Pneu.objects.select_for_update().filter(pk__in=[l.pneu_id for l in lignes])}
        for ligne in lignes:
            ServiceStock.appliquer_mouvement(
                pneu=pneus[ligne.pneu_id],
                quantite=ligne.quantite,
                type_mouvement=MouvementStock.Type.ENTRY,
                motif=f"Réception de l'approvisionnement {approvisionnement.numero}",
                utilisateur=utilisateur,
                approvisionnement=approvisionnement,
            )
        approvisionnement.statut = Approvisionnement.Statut.RECEIVED
        approvisionnement.recu_le = timezone.now()
        approvisionnement.save(update_fields=["statut", "recu_le", "date_modification"])
        return approvisionnement

