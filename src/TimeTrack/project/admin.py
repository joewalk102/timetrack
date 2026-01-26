from django.contrib import admin

from project.models import Project, TimeEntry


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ["name"]
    list_filter = ("created_at", "updated_at")


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "start_time", "end_time")
    search_fields = ("project__name", "user__username")
    list_filter = ("start_time", "end_time")
