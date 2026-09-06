from django.contrib import admin

from .models import Categorie, Marque, MouvementStock, Pneu


@admin.register(Pneu)
class PneuAdmin(admin.ModelAdmin):
    list_display = ["reference_interne", "marque", "modele", "dimension_complete", "prix_vente", "quantite_disponible", "statut"]
    search_fields = ["reference_interne", "reference_commerciale", "modele", "dimension_complete"]
    list_filter = ["marque", "categorie", "saison", "statut"]
    readonly_fields = ["quantite_disponible", "date_creation", "date_modification"]


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ["pneu", "type_mouvement", "quantite", "stock_avant", "stock_apres", "utilisateur", "date_heure"]
    list_filter = ["type_mouvement", "date_heure"]
    readonly_fields = ["pneu", "type_mouvement", "quantite", "stock_avant", "stock_apres", "motif", "commande", "approvisionnement", "utilisateur", "date_heure"]


admin.site.register(Marque)
admin.site.register(Categorie)

