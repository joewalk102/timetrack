from django.urls import path

from project import views

app_name = "project"

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:project_id>/listItem/", views.hx_list_item, name="hx_list_item"),
    path("<int:project_id>/detail/", views.project_detail, name="project_detail"),
    path("new/", views.hx_new_project, name="hx_new_project"),
    path("<int:project_id>/delete/", views.delete_project, name="delete_project"),
]
