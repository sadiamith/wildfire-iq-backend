from django.contrib import admin
from .models import Wildfire

# Register your models here.


@admin.register(Wildfire)
class WildfireAdmin(admin.ModelAdmin):
    list_display = [
        "fire_id",
        "fire_name",
        "status",
        "size_hectares",
        "detected_date",
        "data_source",
    ]
    list_filter = ["status", "data_source", "detected_date"]
    search_fields = ["fire_id", "fire_name", "location_description"]
    readonly_fields = ["created_at", "last_updated"]

    fieldsets = (
        ("Identification", {"fields": ("fire_id", "fire_name", "data_source")}),
        ("Location", {"fields": ("latitude", "longitude", "location_description")}),
        ("Fire Details", {"fields": ("status", "size_hectares", "cause")}),
        ("Timestamps", {"fields": ("detected_date", "created_at", "last_updated")}),
    )
