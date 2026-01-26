from django.urls import path

from calview import views

app_name = "calview"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "htmx/weekly_calendar_data/",
        views.hx_weekly_calendar_data,
        name="hx_weekly_calendar_data",
    ),
]
