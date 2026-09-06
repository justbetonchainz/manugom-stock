from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("pneu/<int:pk>/", views.detail, name="detail"),
    path("marques/", views.brands, name="brands"),
]

