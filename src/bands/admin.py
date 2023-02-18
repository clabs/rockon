from __future__ import annotations

from django.contrib import admin

from .models import Band, BandMember, Stage, TimeSlot


class BandAdmin(admin.ModelAdmin):
    list_display = ("name", "contact", "event", "id")
    list_filter = ("event",)
    search_fields = ("name", "contact__username", "event__name")
    readonly_fields = ("id", "created_at", "updated_at")


admin.site.register(Band, BandAdmin)
admin.site.register(BandMember)
admin.site.register(Stage)
admin.site.register(TimeSlot)
