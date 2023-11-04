from __future__ import annotations

from library.custom_admin import CustomAdminModel, admin

from .models import Band, BandMember, Stage, TimeSlot


class TimeslotAdmin(CustomAdminModel):
    list_display = ("__str__", "start", "end", "band", "id")
    list_filter = ("stage",)
    search_fields = ("stage__name",)
    ordering = ("day", "start", "end", "stage")


class BandAdmin(CustomAdminModel):
    list_display = ("name", "contact", "_has_techrider", "slot", "event", "id")
    list_filter = ("event",)
    search_fields = ("name", "contact__username", "event__name")
    readonly_fields = ("_band_members", "slot")

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


class BandMemberAdmin(CustomAdminModel):
    list_display = ("_user", "band", "position", "updated_at")
    list_filter = ("band",)
    search_fields = ("user__username", "band__name")
    readonly_fields = (
        "user",
        "band",
    )

    def _user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


admin.site.register(Band, BandAdmin)
admin.site.register(BandMember, BandMemberAdmin)
admin.site.register(Stage)
admin.site.register(TimeSlot, TimeslotAdmin)
