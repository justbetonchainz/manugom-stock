from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ProfilUtilisateur, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Rôle MANUGOM", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Rôle MANUGOM", {"fields": ("email", "role")}),)
    list_display = ["username", "email", "role", "is_active", "is_staff"]
    list_filter = ["role", "is_active"]


admin.site.register(ProfilUtilisateur)

