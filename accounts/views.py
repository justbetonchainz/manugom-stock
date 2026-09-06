from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ClientProfileForm, ClientRegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:post_login")
    form = ClientRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Votre compte client est prêt.")
        return redirect("inventory:catalog")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def post_login(request):
    if request.user.is_manager:
        return redirect("dashboard:index")
    return redirect("inventory:catalog")


@login_required
def profile(request):
    if not hasattr(request.user, "client"):
        return redirect("accounts:post_login")
    form = ClientProfileForm(request.POST or None, instance=request.user.client)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})

