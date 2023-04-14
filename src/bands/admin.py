from __future__ import annotations

from django.contrib import admin

from .models import Band, BandMember, Stage, TimeSlot


class TimeslotAdmin(admin.ModelAdmin):
    list_display = ("__str__", "start", "end", "band", "id")
    list_filter = ("stage",)
    search_fields = ("stage__name",)
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("day", "start", "end", "stage")


class BandAdmin(admin.ModelAdmin):
    list_display = ("name", "contact", "slot", "event", "id")
    list_filter = ("event",)
    search_fields = ("name", "contact__username", "event__name")
    readonly_fields = ("id", "created_at", "updated_at", "slot")


class BandMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "band", "position", "updated_at")
    list_filter = ("band",)
    search_fields = ("user__username", "band__name")
    readonly_fields = ("id", "created_at", "updated_at", "user", "band")


admin.site.register(Band, BandAdmin)
admin.site.register(BandMember, BandMemberAdmin)
admin.site.register(Stage)
admin.site.register(TimeSlot, TimeslotAdmin)
