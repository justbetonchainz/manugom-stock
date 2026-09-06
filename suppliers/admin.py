from django.contrib import admin

from .models import Approvisionnement, Fournisseur, LigneApprovisionnement


class LigneApproInline(admin.TabularInline):
    model = LigneApprovisionnement
    extra = 1


@admin.register(Approvisionnement)
class ApprovisionnementAdmin(admin.ModelAdmin):
    list_display = ["numero", "fournisseur", "statut", "montant_total", "recu_le"]
    list_filter = ["statut", "date"]
    readonly_fields = ["numero", "montant_total", "recu_le"]
    inlines = [LigneApproInline]


admin.site.register(Fournisseur)

