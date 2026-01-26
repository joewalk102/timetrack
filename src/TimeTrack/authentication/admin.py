from django.contrib import admin


@admin.register
class TTUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "timezone", "dark_mode")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "dark_mode")
