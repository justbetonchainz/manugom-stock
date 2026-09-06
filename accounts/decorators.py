from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def manager_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_manager:
            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cet espace.")
            return redirect("core:home")
        return view_func(request, *args, **kwargs)

    return wrapped


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_superuser and request.user.role != request.user.Role.ADMIN:
            messages.error(request, "Cette action est réservée aux administrateurs.")
            return redirect("dashboard:index")
        return view_func(request, *args, **kwargs)

    return wrapped

