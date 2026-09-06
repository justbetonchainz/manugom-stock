from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("panier/", views.cart, name="cart"),
    path("panier/ajouter/<int:pneu_id>/", views.add_to_cart, name="add"),
    path("panier/modifier/<int:line_id>/", views.update_cart, name="update"),
    path("panier/retirer/<int:line_id>/", views.remove_from_cart, name="remove"),
    path("panier/vider/", views.clear_cart, name="clear"),
    path("valider/", views.checkout, name="checkout"),
    path("mes-commandes/", views.order_list, name="list"),
    path("<int:pk>/", views.order_detail, name="detail"),
    path("<int:pk>/annuler/", views.cancel_order, name="cancel"),
]

