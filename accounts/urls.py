from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("connexion/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("inscription/", views.register, name="register"),
    path("apres-connexion/", views.post_login, name="post_login"),
    path("profil/", views.profile, name="profile"),
    path("mot-de-passe/", auth_views.PasswordChangeView.as_view(template_name="accounts/password_change.html", success_url="/comptes/profil/"), name="password_change"),
    path("mot-de-passe-oublie/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html", email_template_name="accounts/password_reset_email.txt", success_url="/comptes/connexion/"), name="password_reset"),
    path("reinitialiser/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html", success_url="/comptes/connexion/"), name="password_reset_confirm"),
]
