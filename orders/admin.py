from django.contrib import admin

from .models import Commande, LigneCommande, LignePanier, Panier


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ["pneu", "reference_pneu", "marque", "modele", "dimension", "quantite", "prix_unitaire", "sous_total"]


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ["numero", "client", "date", "statut", "statut_paiement", "montant_total"]
    search_fields = ["numero", "client__numero", "client__email"]
    list_filter = ["statut", "statut_paiement", "type_reception"]
    readonly_fields = ["numero", "montant_total", "stock_retire", "stock_restaure"]
    inlines = [LigneCommandeInline]


admin.site.register(Panier)
admin.site.register(LignePanier)

