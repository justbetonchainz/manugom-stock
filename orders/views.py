from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from inventory.models import Pneu

from .forms import CheckoutForm
from .models import Commande, LignePanier, Panier
from .services import ALLOWED_TRANSITIONS, ServiceCommande


def _client(request):
    return getattr(request.user, "client", None)


def _active_cart(client):
    panier, _ = Panier.objects.get_or_create(client=client, actif=True)
    return panier


@require_POST
def add_to_cart(request, pneu_id):
    if not request.user.is_authenticated:
        messages.info(request, "Connectez-vous avec un compte client pour ajouter ce pneu au panier.")
        return redirect_to_login(reverse("inventory:detail", args=[pneu_id]))
    client = _client(request)
    if not client:
        messages.error(request, "Seuls les comptes clients disposent d'un panier.")
        return redirect("inventory:catalog")
    pneu = get_object_or_404(Pneu, pk=pneu_id, statut=Pneu.Statut.ACTIVE)
    try:
        qty = int(request.POST.get("quantite", 1))
    except (TypeError, ValueError):
        qty = 0
    panier = _active_cart(client)
    ligne = LignePanier.objects.filter(panier=panier, pneu=pneu).first()
    cible = qty + (ligne.quantite if ligne else 0)
    if qty <= 0 or cible > pneu.quantite_disponible:
        messages.error(request, "Quantité invalide ou supérieure au stock disponible.")
    else:
        LignePanier.objects.update_or_create(panier=panier, pneu=pneu, defaults={"quantite": cible})
        messages.success(request, f"{pneu.reference_interne} ajouté au panier.")
    return redirect(request.POST.get("next") or "orders:cart")


@login_required
def cart(request):
    client = _client(request)
    if not client:
        return redirect("inventory:catalog")
    panier = _active_cart(client)
    return render(request, "orders/cart.html", {"panier": panier, "lignes": panier.lignes.select_related("pneu", "pneu__marque")})


@login_required
@require_POST
def update_cart(request, line_id):
    client = _client(request)
    ligne = get_object_or_404(LignePanier.objects.select_related("pneu", "panier"), pk=line_id, panier__client=client, panier__actif=True)
    try:
        qty = int(request.POST.get("quantite", 0))
    except (TypeError, ValueError):
        qty = 0
    if 1 <= qty <= ligne.pneu.quantite_disponible:
        ligne.quantite = qty
        ligne.save(update_fields=["quantite"])
        messages.success(request, "Quantité mise à jour.")
    else:
        messages.error(request, "Quantité invalide ou stock insuffisant.")
    return redirect("orders:cart")


@login_required
@require_POST
def remove_from_cart(request, line_id):
    client = _client(request)
    get_object_or_404(LignePanier, pk=line_id, panier__client=client, panier__actif=True).delete()
    messages.success(request, "Article retiré du panier.")
    return redirect("orders:cart")


@login_required
@require_POST
def clear_cart(request):
    client = _client(request)
    if client:
        _active_cart(client).lignes.all().delete()
        messages.success(request, "Panier vidé.")
    return redirect("orders:cart")


@login_required
def checkout(request):
    client = _client(request)
    if not client:
        return redirect("inventory:catalog")
    panier = _active_cart(client)
    if not panier.lignes.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect("orders:cart")
    initial = {"adresse": client.adresse, "ville": client.ville}
    form = CheckoutForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            commande = ServiceCommande.creer_depuis_panier(panier=panier, **form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, f"Commande {commande.numero} enregistrée. Elle attend confirmation.")
            return redirect("orders:detail", pk=commande.pk)
    return render(request, "orders/checkout.html", {"form": form, "panier": panier})


@login_required
def order_list(request):
    client = _client(request)
    if not client:
        return redirect("dashboard:index")
    return render(request, "orders/order_list.html", {"commandes": client.commandes.prefetch_related("lignes")})


@login_required
def order_detail(request, pk):
    client = _client(request)
    if client:
        commande = get_object_or_404(Commande.objects.prefetch_related("lignes"), pk=pk, client=client)
    elif request.user.is_manager:
        commande = get_object_or_404(Commande.objects.prefetch_related("lignes"), pk=pk)
    else:
        return redirect("core:home")
    return render(request, "orders/order_detail.html", {
        "commande": commande,
        "is_owner": bool(client),
        "allowed_statuses": [(value, label) for value, label in Commande.Statut.choices if value in ALLOWED_TRANSITIONS.get(commande.statut, set())],
    })


@login_required
@require_POST
def cancel_order(request, pk):
    client = _client(request)
    commande = get_object_or_404(Commande, pk=pk, client=client)
    try:
        ServiceCommande.annuler(commande=commande, utilisateur=request.user)
        messages.success(request, "Commande annulée.")
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    return redirect("orders:detail", pk=pk)
