from django.shortcuts import render

from inventory.models import Marque, Pneu


def home(request):
    return render(
        request,
        "core/home.html",
        {
            "marques": Marque.objects.filter(actif=True)[:8],
            "pneus": Pneu.objects.filter(statut=Pneu.Statut.ACTIVE, quantite_disponible__gt=0).select_related("marque")[:4],
        },
    )


def services(request):
    return render(request, "core/services.html")


def about(request):
    return render(request, "core/about.html")

