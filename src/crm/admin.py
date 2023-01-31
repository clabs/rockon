from __future__ import annotations

from django.contrib import admin

# WONTFIX: stop black and isort from fighting each other
# fmt: off
from .models import (
    EmailVerification,
    MagicLink,
    Organisation,
    Sponsoring,
    Type,
    UserProfile,
)

# fmt: on


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "id", "created_at")
    readonly_fields = ("created_at", "updated_at")


class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ("user", "id", "created_at", "expires_at")
    readonly_fields = ("created_at", "updated_at")


admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(MagicLink, MagicLinkAdmin)
admin.site.register(Organisation)
admin.site.register(Sponsoring)
admin.site.register(Type)
admin.site.register(UserProfile)
