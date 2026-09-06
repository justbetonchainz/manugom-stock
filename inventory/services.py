from django.core.exceptions import ValidationError
from django.db import transaction

from .models import MouvementStock, Pneu


class ServiceStock:
    """Point d'entrée unique pour toute modification de quantité en stock."""

    @staticmethod
    def appliquer_mouvement(*, pneu, quantite, type_mouvement, motif, utilisateur, commande=None, approvisionnement=None):
        if quantite <= 0:
            raise ValidationError("La quantité du mouvement doit être strictement positive.")
        with transaction.atomic():
            locked = Pneu.objects.select_for_update().get(pk=pneu.pk)
            stock_avant = locked.quantite_disponible
            sorties = {MouvementStock.Type.EXIT, MouvementStock.Type.ADJUST_DOWN}
            stock_apres = stock_avant - quantite if type_mouvement in sorties else stock_avant + quantite
            if stock_apres < 0:
                raise ValidationError(f"Stock insuffisant pour {locked.reference_interne}.")
            locked.quantite_disponible = stock_apres
            locked.save(update_fields=["quantite_disponible", "date_modification"])
            mouvement = MouvementStock.objects.create(
                pneu=locked,
                type_mouvement=type_mouvement,
                quantite=quantite,
                stock_avant=stock_avant,
                stock_apres=stock_apres,
                motif=motif,
                commande=commande,
                approvisionnement=approvisionnement,
                utilisateur=utilisateur,
            )
        pneu.quantite_disponible = stock_apres
        return mouvement

