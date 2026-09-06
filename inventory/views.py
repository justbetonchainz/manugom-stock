from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Categorie, Marque, Pneu


SORTS = {
    "prix_asc": "prix_vente",
    "prix_desc": "-prix_vente",
    "marque": "marque__nom",
    "nouveautes": "-date_creation",
    "disponibilite": "-quantite_disponible",
}


def catalog(request):
    pneus = Pneu.objects.filter(statut=Pneu.Statut.ACTIVE).select_related("marque", "categorie")
    keyword = request.GET.get("q", "").strip()
    reference = request.GET.get("reference", "").strip()
    if keyword:
        pneus = pneus.filter(Q(modele__icontains=keyword) | Q(description__icontains=keyword) | Q(usage_vehicule__icontains=keyword) | Q(marque__nom__icontains=keyword))
    if reference:
        pneus = pneus.filter(reference_interne__icontains=reference)
    for key, field in [("marque", "marque_id"), ("categorie", "categorie_id"), ("largeur", "largeur"), ("hauteur", "hauteur"), ("diametre", "diametre"), ("saison", "saison")]:
        value = request.GET.get(key)
        if value:
            pneus = pneus.filter(**{field: value})
    if request.GET.get("disponibilite") == "en_stock":
        pneus = pneus.filter(quantite_disponible__gt=0)
    elif request.GET.get("disponibilite") == "rupture":
        pneus = pneus.filter(quantite_disponible=0)
    for param, lookup in [("prix_min", "prix_vente__gte"), ("prix_max", "prix_vente__lte")]:
        try:
            if request.GET.get(param):
                pneus = pneus.filter(**{lookup: Decimal(request.GET[param])})
        except InvalidOperation:
            pass
    pneus = pneus.order_by(SORTS.get(request.GET.get("tri"), "marque__nom"), "modele")
    page = Paginator(pneus, 9).get_page(request.GET.get("page"))
    context = {
        "page_obj": page,
        "marques": Marque.objects.filter(actif=True),
        "categories": Categorie.objects.filter(actif=True),
        "largeurs": Pneu.objects.filter(statut=Pneu.Statut.ACTIVE).values_list("largeur", flat=True).distinct().order_by("largeur"),
        "hauteurs": Pneu.objects.filter(statut=Pneu.Statut.ACTIVE).values_list("hauteur", flat=True).distinct().order_by("hauteur"),
        "diametres": Pneu.objects.filter(statut=Pneu.Statut.ACTIVE).values_list("diametre", flat=True).distinct().order_by("diametre"),
        "saisons": Pneu.Saison.choices,
        "sorts": [(k, v.replace("_", " ").title()) for k, v in [("prix_asc", "Prix croissant"), ("prix_desc", "Prix décroissant"), ("marque", "Marque"), ("nouveautes", "Nouveautés"), ("disponibilite", "Disponibilité")]],
    }
    return render(request, "inventory/catalog.html", context)


def detail(request, pk):
    pneu = get_object_or_404(Pneu.objects.select_related("marque", "categorie"), pk=pk, statut=Pneu.Statut.ACTIVE)
    similaires = Pneu.objects.filter(categorie=pneu.categorie, statut=Pneu.Statut.ACTIVE).exclude(pk=pneu.pk).select_related("marque")[:4]
    return render(request, "inventory/detail.html", {"pneu": pneu, "similaires": similaires})


def brands(request):
    return render(request, "inventory/brands.html", {"marques": Marque.objects.filter(actif=True).prefetch_related("pneus")})

