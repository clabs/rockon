from __future__ import annotations

from django.contrib import admin

from .models import Bid, Event, Media, Region, Track, User, Vote


class BidAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bandname",
        "managed",
        "student",
        "region",
        "event",
        "created",
        "modified",
    )

    search_fields = ("bandname",)

    list_filter = ("managed", "student", "region", "event")

    readonly_fields = ("id", "created", "modified")


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "opening_date",
        "closing_date",
        "created",
        "modified",
    )

    readonly_fields = ("id", "created", "modified")


class MediaAddmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filename",
        "bid",
        "type",
        "created",
        "modified",
    )

    list_filter = ("type", "bid", "bid__event__name")

    readonly_fields = ("id", "created", "modified")


class RegionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created",
        "modified",
    )

    readonly_fields = ("id", "created", "modified")


class TrackAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "event",
        "visible",
        "created",
        "modified",
    )

    list_filter = ("event__name", "visible")

    readonly_fields = ("id", "created", "modified")


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "role",
        "provider",
        "created",
        "modified",
    )

    list_filter = ("role", "provider")

    readonly_fields = ("id", "created", "modified")


class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "bid",
        "user",
        "created",
        "modified",
    )

    list_filter = ("bid__event__name", "user__name")

    readonly_fields = ("id", "created", "modified")


admin.site.register(Bid, BidAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Media, MediaAddmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Vote, VoteAdmin)
