from django.urls import path

from project import views

app_name = "project"

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:project_id>/listItem/", views.hx_list_item, name="hx_list_item"),
    path("<int:project_id>/detail/", views.project_detail, name="project_detail"),
]
