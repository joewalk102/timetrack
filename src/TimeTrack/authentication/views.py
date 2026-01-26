from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_http_methods
from pytz import common_timezones


# Create your views here.
def login(request):
    """
    Renders and processes a Bootstrap-styled login form using Django's AuthenticationForm.
    """
    if request.method == "POST":
        next_url = request.GET.get("next", "project:home")
        form = AuthenticationForm(request, data=request.POST)
        # add Bootstrap classes to widgets

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)
    form.fields["username"].widget.attrs.update(
        {
            "class": "form-control",
            "placeholder": "Username",
            "autofocus": "autofocus",
        }
    )
    form.fields["password"].widget.attrs.update(
        {"class": "form-control", "placeholder": "Password"}
    )

    return render(request, "authentication/login.html", {"form": form})


def logout(request):
    auth_logout(request)
    return redirect("project:home")


@login_required
def settings_page(request):
    """Display user settings page."""
    timezones = common_timezones
    return render(
        request,
        "authentication/settings.html",
        {"timezones": timezones, "user": request.user},
    )


@login_required
@require_http_methods(["POST"])
def update_settings(request):
    """Update user settings (timezone and dark mode)."""
    user = request.user
    user.timezone = request.POST.get("timezone", user.timezone)
    user.dark_mode = request.POST.get("dark_mode") == "on"
    user.save()
    messages.success(request, "Settings updated successfully.")
    return redirect("authentication:settings_page")
