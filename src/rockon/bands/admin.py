from __future__ import annotations

from rockon.library.custom_admin import CustomAdminModel, admin

from .models import Band, BandMedia, BandMember, BandVote, Stage, TimeSlot, Track


class TimeslotAdmin(CustomAdminModel):
    list_display = ("__str__", "start", "end", "band", "get_event_name")
    list_filter = ("stage__name", "stage__event__name")
    search_fields = ("stage__name",)
    ordering = ("day", "start", "end", "stage")

    def get_event_name(self, obj):
        return obj.stage.event

    get_event_name.short_description = "Event"


class BandAdmin(CustomAdminModel):
    list_display = (
        "__str__",
        "contact",
        "bid_status",
        "bid_complete",
        "_has_techrider",
        "track",
        "slot",
        "event",
    )
    list_filter = (
        "event__name",
        "bid_status",
        "bid_complete",
    )
    search_fields = ("name", "contact__username", "event__name")
    readonly_fields = (
        "_band_members",
        "slot",
        "guid",
    )

    def _band_members(self, obj):
        return ", ".join(
            [
                f"{member.user.first_name} {member.user.last_name}"
                for member in obj.band_members.all()
            ]
        )

    def _has_techrider(self, obj):
        return obj.techrider != {}

    _has_techrider.boolean = True

    def bid_complete(self, obj):
        return obj.bid_complete

    bid_complete.boolean = True


class BandMemberAdmin(CustomAdminModel):
    list_display = ("_user", "band", "position", "updated_at")
    list_filter = ("band__name",)
    search_fields = ("user__username", "band__name")
    readonly_fields = (
        "user",
        "band",
    )

    def _user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class BandMediaAdmin(CustomAdminModel):
    list_display = (
        "band",
        "media_type",
        "url",
        "file_name_original",
        "file",
        "thumbnail",
    )
    list_filter = ("band__name", "media_type")
    search_fields = ("band__name", "media_type", "url", "file", "thumbnail")
    readonly_fields = (
        "band",
        "media_type",
        "thumbnail",
    )


class StageAdmin(CustomAdminModel):
    list_display = ("name", "event", "id")
    list_filter = ("event__name",)
    search_fields = ("name", "event__name")


class TrackAdmin(CustomAdminModel):
    list_display = ("name", "id")
    list_filter = ("events__name",)
    search_fields = ("name", "events__name")


class BandVoteAdmin(CustomAdminModel):
    list_display = ("band", "user", "created_at", "event")
    list_filter = ("event",)
    search_fields = ("band__name", "user__username")


admin.site.register(Band, BandAdmin)
admin.site.register(BandMedia, BandMediaAdmin)
admin.site.register(BandMember, BandMemberAdmin)
admin.site.register(BandVote, BandVoteAdmin)
admin.site.register(Stage, StageAdmin)
admin.site.register(TimeSlot, TimeslotAdmin)
admin.site.register(Track, TrackAdmin)
