from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required, manager_required
from accounts.models import User
from customers.models import Client
from inventory.forms import CategorieForm, MarqueForm, MouvementForm, PneuForm
from inventory.models import Categorie, Marque, MouvementStock, Pneu
from inventory.services import ServiceStock
from orders.models import Commande, LigneCommande
from orders.services import ALLOWED_TRANSITIONS, ServiceCommande
from quotes.models import DemandeDevis, MessageContact
from suppliers.models import Approvisionnement, Fournisseur
from suppliers.services import ServiceApprovisionnement

from .forms import ApprovisionnementForm, ClientAdminForm, EmployeeCreationForm, FournisseurForm, LigneApproFormSet


def _chart(items, label_key, value_key):
    return {"labels": [str(i[label_key]) for i in items], "values": [float(i[value_key] or 0) for i in items]}


@manager_required
def index(request):
    today = timezone.localdate()
    value_expr = ExpressionWrapper(F("quantite_disponible") * F("prix_achat"), output_field=DecimalField(max_digits=14, decimal_places=2))
    sales_by_month = list(
        Commande.objects.exclude(statut=Commande.Statut.CANCELLED)
        .annotate(mois=TruncMonth("date"))
        .values("mois")
        .annotate(total=Sum("montant_total"))
        .order_by("mois")
    )[-12:]
    brands = list(Pneu.objects.values("marque__nom").annotate(total=Sum("quantite_disponible")).order_by("marque__nom"))
    statuses = list(Commande.objects.values("statut").annotate(total=Count("id")).order_by("statut"))
    top = list(
        LigneCommande.objects.exclude(commande__statut=Commande.Statut.CANCELLED)
        .values("reference_pneu")
        .annotate(total=Sum("quantite"))
        .order_by("-total")[:5]
    )
    movements = list(
        MouvementStock.objects.annotate(mois=TruncMonth("date_heure"))
        .values("mois", "type_mouvement")
        .annotate(total=Sum("quantite"))
        .order_by("mois")
    )[-24:]
    stats = {
        "references": Pneu.objects.filter(statut=Pneu.Statut.ACTIVE).count(),
        "stock_total": Pneu.objects.aggregate(v=Sum("quantite_disponible"))["v"] or 0,
        "valeur_stock": Pneu.objects.aggregate(v=Sum(value_expr))["v"] or Decimal("0"),
        "clients": Client.objects.filter(actif=True).count(),
        "commandes_jour": Commande.objects.filter(date__date=today).count(),
        "en_attente": Commande.objects.filter(statut=Commande.Statut.PENDING).count(),
        "livrees": Commande.objects.filter(statut=Commande.Statut.DELIVERED).count(),
        "chiffre_affaires": Commande.objects.filter(statut=Commande.Statut.DELIVERED).aggregate(v=Sum("montant_total"))["v"] or Decimal("0"),
        "stock_faible": Pneu.objects.filter(quantite_disponible__gt=0, quantite_disponible__lte=F("seuil_minimum")).count(),
        "ruptures": Pneu.objects.filter(quantite_disponible=0, statut=Pneu.Statut.ACTIVE).count(),
    }
    chart_data = {
        "sales": {"labels": [i["mois"].strftime("%m/%Y") for i in sales_by_month], "values": [float(i["total"] or 0) for i in sales_by_month]},
        "brands": _chart(brands, "marque__nom", "total"),
        "statuses": _chart(statuses, "statut", "total"),
        "top": _chart(top, "reference_pneu", "total"),
        "movements": {
            "labels": [f'{i["mois"].strftime("%m/%Y")} · {i["type_mouvement"]}' for i in movements],
            "values": [float(i["total"] or 0) for i in movements],
        },
    }
    return render(request, "dashboard/index.html", {"stats": stats, "recentes": Commande.objects.select_related("client")[:8], "top_pneus": top, "chart_data": chart_data})


def _form_page(request, form_class, *, instance=None, title, success_name, success_message):
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect(success_name)
    return render(request, "dashboard/form.html", {"form": form, "title": title})


@manager_required
def tire_list(request):
    query = request.GET.get("q", "")
    pneus = Pneu.objects.select_related("marque", "categorie")
    if query:
        pneus = pneus.filter(Q(reference_interne__icontains=query) | Q(modele__icontains=query) | Q(marque__nom__icontains=query))
    return render(request, "dashboard/tire_list.html", {"pneus": pneus, "query": query})


@manager_required
def tire_create(request):
    return _form_page(request, PneuForm, title="Ajouter une référence de pneu", success_name="dashboard:tires", success_message="Pneu ajouté. Enregistrez ensuite son stock initial par un mouvement.")


@manager_required
def tire_edit(request, pk):
    return _form_page(request, PneuForm, instance=get_object_or_404(Pneu, pk=pk), title="Modifier le pneu", success_name="dashboard:tires", success_message="Pneu modifié.")


@manager_required
@require_POST
def tire_archive(request, pk):
    pneu = get_object_or_404(Pneu, pk=pk)
    pneu.statut = Pneu.Statut.ARCHIVED
    pneu.save(update_fields=["statut", "date_modification"])
    messages.success(request, "Pneu archivé sans supprimer son historique.")
    return redirect("dashboard:tires")


@manager_required
def brand_list(request):
    return render(request, "dashboard/simple_list.html", {"title": "Marques", "objects": Marque.objects.all(), "create_url": reverse("dashboard:brand_create"), "edit_name": "dashboard:brand_edit", "kind": "brand"})


@manager_required
def brand_create(request):
    return _form_page(request, MarqueForm, title="Ajouter une marque", success_name="dashboard:brands", success_message="Marque ajoutée.")


@manager_required
def brand_edit(request, pk):
    return _form_page(request, MarqueForm, instance=get_object_or_404(Marque, pk=pk), title="Modifier la marque", success_name="dashboard:brands", success_message="Marque modifiée.")


@manager_required
@require_POST
def brand_archive(request, pk):
    brand = get_object_or_404(Marque, pk=pk)
    brand.actif = False
    brand.save(update_fields=["actif", "date_modification"])
    messages.success(request, "Marque archivée; les références existantes sont conservées.")
    return redirect("dashboard:brands")


@manager_required
def category_list(request):
    return render(request, "dashboard/simple_list.html", {"title": "Catégories", "objects": Categorie.objects.all(), "create_url": reverse("dashboard:category_create"), "edit_name": "dashboard:category_edit", "kind": "category"})


@manager_required
def category_create(request):
    return _form_page(request, CategorieForm, title="Ajouter une catégorie", success_name="dashboard:categories", success_message="Catégorie ajoutée.")


@manager_required
def category_edit(request, pk):
    return _form_page(request, CategorieForm, instance=get_object_or_404(Categorie, pk=pk), title="Modifier la catégorie", success_name="dashboard:categories", success_message="Catégorie modifiée.")


@manager_required
@require_POST
def category_archive(request, pk):
    category = get_object_or_404(Categorie, pk=pk)
    category.actif = False
    category.save(update_fields=["actif", "date_modification"])
    messages.success(request, "Catégorie archivée; l'historique reste intact.")
    return redirect("dashboard:categories")


@manager_required
def client_list(request):
    return render(request, "dashboard/client_list.html", {"clients": Client.objects.all()})


@manager_required
def client_create(request):
    return _form_page(request, ClientAdminForm, title="Ajouter un client", success_name="dashboard:clients", success_message="Client ajouté.")


@manager_required
def client_edit(request, pk):
    return _form_page(request, ClientAdminForm, instance=get_object_or_404(Client, pk=pk), title="Modifier le client", success_name="dashboard:clients", success_message="Client modifié.")


@manager_required
@require_POST
def client_archive(request, pk):
    Client.objects.filter(pk=pk).update(actif=False)
    messages.success(request, "Client désactivé; son historique est conservé.")
    return redirect("dashboard:clients")


@manager_required
def supplier_list(request):
    return render(request, "dashboard/supplier_list.html", {"fournisseurs": Fournisseur.objects.prefetch_related("marques_fournies")})


@manager_required
def supplier_create(request):
    return _form_page(request, FournisseurForm, title="Ajouter un fournisseur", success_name="dashboard:suppliers", success_message="Fournisseur ajouté.")


@manager_required
def supplier_edit(request, pk):
    return _form_page(request, FournisseurForm, instance=get_object_or_404(Fournisseur, pk=pk), title="Modifier le fournisseur", success_name="dashboard:suppliers", success_message="Fournisseur modifié.")


@manager_required
@require_POST
def supplier_archive(request, pk):
    supplier = get_object_or_404(Fournisseur, pk=pk)
    supplier.actif = False
    supplier.save(update_fields=["actif", "date_modification"])
    messages.success(request, "Fournisseur archivé.")
    return redirect("dashboard:suppliers")


@manager_required
def order_list(request):
    return render(request, "dashboard/order_list.html", {"commandes": Commande.objects.select_related("client").prefetch_related("lignes")})


@manager_required
@require_POST
def order_status(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    try:
        ServiceCommande.changer_statut(commande=commande, nouveau_statut=request.POST.get("statut"), utilisateur=request.user)
        messages.success(request, "Statut de la commande mis à jour.")
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    return redirect("orders:detail", pk=pk)


@manager_required
def supply_list(request):
    return render(request, "dashboard/supply_list.html", {"approvisionnements": Approvisionnement.objects.select_related("fournisseur", "utilisateur_responsable").prefetch_related("lignes")})


@manager_required
@transaction.atomic
def supply_create(request):
    supply = Approvisionnement(utilisateur_responsable=request.user)
    form = ApprovisionnementForm(request.POST or None, instance=supply)
    formset = LigneApproFormSet(request.POST or None, instance=supply)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        supply = form.save(commit=False)
        supply.utilisateur_responsable = request.user
        supply.save()
        formset.instance = supply
        formset.save()
        supply.recalculer_total()
        messages.success(request, f"Approvisionnement {supply.numero} créé.")
        return redirect("dashboard:supplies")
    return render(request, "dashboard/supply_form.html", {"form": form, "formset": formset})


@manager_required
@transaction.atomic
def supply_edit(request, pk):
    supply = get_object_or_404(Approvisionnement, pk=pk)
    if supply.statut not in {Approvisionnement.Statut.DRAFT, Approvisionnement.Statut.ORDERED}:
        messages.error(request, "Un approvisionnement reçu ou annulé ne peut plus être modifié.")
        return redirect("dashboard:supplies")
    form = ApprovisionnementForm(request.POST or None, instance=supply)
    formset = LigneApproFormSet(request.POST or None, instance=supply)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        supply.recalculer_total()
        messages.success(request, f"Approvisionnement {supply.numero} modifié.")
        return redirect("dashboard:supplies")
    return render(request, "dashboard/supply_form.html", {"form": form, "formset": formset, "supply": supply})


@manager_required
@require_POST
def supply_cancel(request, pk):
    supply = get_object_or_404(Approvisionnement, pk=pk)
    if supply.statut in {Approvisionnement.Statut.DRAFT, Approvisionnement.Statut.ORDERED}:
        supply.statut = Approvisionnement.Statut.CANCELLED
        supply.save(update_fields=["statut", "date_modification"])
        messages.success(request, "Approvisionnement annulé sans suppression d'historique.")
    else:
        messages.error(request, "Cet approvisionnement ne peut plus être annulé.")
    return redirect("dashboard:supplies")


@manager_required
@require_POST
def supply_receive(request, pk):
    supply = get_object_or_404(Approvisionnement, pk=pk)
    try:
        ServiceApprovisionnement.receptionner(approvisionnement=supply, utilisateur=request.user)
        messages.success(request, "Approvisionnement reçu et stock mis à jour.")
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    return redirect("dashboard:supplies")


@manager_required
def movement_list(request):
    return render(request, "dashboard/movement_list.html", {"mouvements": MouvementStock.objects.select_related("pneu", "utilisateur")[:200]})


@manager_required
def movement_create(request):
    form = MouvementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            ServiceStock.appliquer_mouvement(utilisateur=request.user, **form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Mouvement enregistré et stock recalculé.")
            return redirect("dashboard:movements")
    return render(request, "dashboard/form.html", {"form": form, "title": "Enregistrer un mouvement de stock"})


@manager_required
def alerts(request):
    pneus = Pneu.objects.filter(statut=Pneu.Statut.ACTIVE, quantite_disponible__lte=F("seuil_minimum")).select_related("marque").order_by("quantite_disponible")
    return render(request, "dashboard/alerts.html", {"pneus": pneus})


@manager_required
def quote_list(request):
    return render(request, "dashboard/inbox.html", {"title": "Demandes de devis", "objects": DemandeDevis.objects.all(), "kind": "quote"})


@manager_required
def contact_list(request):
    return render(request, "dashboard/inbox.html", {"title": "Messages de contact", "objects": MessageContact.objects.all(), "kind": "contact"})


@manager_required
@require_POST
def quote_status(request, pk):
    quote = get_object_or_404(DemandeDevis, pk=pk)
    if request.POST.get("statut") in DemandeDevis.Statut.values:
        quote.statut = request.POST["statut"]
        quote.save(update_fields=["statut"])
        messages.success(request, "Statut du devis mis à jour.")
    return redirect("dashboard:quotes")


@manager_required
@require_POST
def contact_toggle(request, pk):
    contact = get_object_or_404(MessageContact, pk=pk)
    contact.lu = not contact.lu
    contact.save(update_fields=["lu"])
    messages.success(request, "Statut de lecture mis à jour.")
    return redirect("dashboard:contacts")


@admin_required
def user_list(request):
    return render(request, "dashboard/user_list.html", {"users": User.objects.all().order_by("role", "username")})


@admin_required
def employee_create(request):
    return _form_page(request, EmployeeCreationForm, title="Créer un compte employé", success_name="dashboard:users", success_message="Compte employé créé.")


@admin_required
@require_POST
def user_toggle(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user or user.is_superuser:
        messages.error(request, "Ce compte administrateur ne peut pas être désactivé ici.")
    else:
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.success(request, "Statut du compte mis à jour.")
    return redirect("dashboard:users")

