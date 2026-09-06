from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["numero", "nom", "prenom", "telephone", "email", "ville", "actif"]
    search_fields = ["numero", "nom", "prenom", "email", "telephone"]
    list_filter = ["type_client", "actif", "ville"]

