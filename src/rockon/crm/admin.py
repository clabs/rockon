from __future__ import annotations

from rockon.library.custom_admin import CustomAdminModel, admin

from .models import (
    AccountContext,
    EmailVerification,
    MagicLink,
    Organisation,
    Sponsoring,
    Type,
    UserProfile,
)


class UserProfileAdmin(CustomAdminModel):
    list_display = (
        "_user",
        "nick_name",
        "email_is_verified",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("user",)
    search_fields = ("user__first_name", "user__last_name", "user__email")

    def _user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class EmailVerificationAdmin(CustomAdminModel):
    list_display = ("user", "id", "created_at")


class MagicLinkAdmin(CustomAdminModel):
    list_display = ("user", "id", "created_at", "expires_at")


admin.site.register(AccountContext)
admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(MagicLink, MagicLinkAdmin)
admin.site.register(Organisation)
admin.site.register(Sponsoring)
admin.site.register(Type)
admin.site.register(UserProfile, UserProfileAdmin)
