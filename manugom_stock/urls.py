from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "MANUGOM Stock — Administration Django"
admin.site.site_title = "MANUGOM Stock"
admin.site.index_title = "Gestion du magasin"

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("comptes/", include("accounts.urls")),
    path("catalogue/", include("inventory.urls")),
    path("commandes/", include("orders.urls")),
    path("gestion/", include("dashboard.urls")),
    path("", include("quotes.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

