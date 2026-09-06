from django.contrib import admin

from .models import DemandeDevis, MessageContact


@admin.register(DemandeDevis)
class DemandeDevisAdmin(admin.ModelAdmin):
    list_display = ["nom_complet", "telephone", "dimensions_recherchees", "quantite", "statut", "date"]
    list_filter = ["statut", "date"]


@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ["nom", "email", "sujet", "lu", "date"]
    list_filter = ["lu", "date"]

