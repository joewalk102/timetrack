from django.urls import path
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from authentication import views

app_name = "authentication"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("settings/", views.settings_page, name="settings_page"),
    path("settings/update/", views.update_settings, name="update_settings"),
    path(
        "password/change/",
        PasswordChangeView.as_view(
            template_name="authentication/password_change.html",
            success_url="/auth/password/change/done/",
        ),
        name="password_change",
    ),
    path(
        "password/change/done/",
        PasswordChangeDoneView.as_view(
            template_name="authentication/password_change_done.html"
        ),
        name="password_change_done",
    ),
]
