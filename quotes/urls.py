from django.urls import path

from . import views

app_name = "quotes"

urlpatterns = [
    path("demande-de-devis/", views.quote_request, name="quote"),
    path("contact/", views.contact, name="contact"),
]

