from __future__ import annotations

from rockon.library.custom_admin import CustomAdminModel, admin

from .models import (
    EmailVerification,
    Event,
    MagicLink,
    Organisation,
    Sponsoring,
    Task,
    Timeline,
    UserProfile,
)


class UserProfileAdmin(CustomAdminModel):
    list_display = (
        "full_name",
        "nick_name",
        "email_is_verified",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("user",)
    search_fields = ("user__first_name", "user__last_name", "user__email")


class EmailVerificationAdmin(CustomAdminModel):
    list_display = ("user", "id", "created_at")


class MagicLinkAdmin(CustomAdminModel):
    list_display = ("user", "id", "created_at", "expires_at")


class EventAdmin(CustomAdminModel):
    list_display = ("name", "slug", "start", "end", "created_at", "updated_at")
    readonly_fields = ("slug",)


class OrganisationAdmin(CustomAdminModel):
    list_display = ("org_name", "org_address", "org_zip", "org_place", "get_contact")
    search_fields = ("org_name", "org_address", "org_zip", "org_place")

    def get_contact(self, obj):
        return obj.members.first()


admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(MagicLink, MagicLinkAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Sponsoring)
admin.site.register(Task)
admin.site.register(Timeline)
admin.site.register(UserProfile, UserProfileAdmin)
