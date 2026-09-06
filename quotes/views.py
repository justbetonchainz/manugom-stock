from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm, DemandeDevisForm


def quote_request(request):
    form = DemandeDevisForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Votre demande de devis a bien été enregistrée.")
        return redirect("quotes:quote")
    return render(request, "quotes/quote.html", {"form": form})


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Votre message a bien été transmis.")
        return redirect("quotes:contact")
    return render(request, "quotes/contact.html", {"form": form})

