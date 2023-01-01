from __future__ import annotations

from django.contrib import admin

# WONTFIX: stop black and isort from fighting each other
# fmt: off
from .models import (EmailVerification, Exhibitor, LinkShortener, MagicLink,
                     Organisation, Person, Sponsoring, Type)

# fmt: on


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("person", "id", "created_at")


class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ("person", "id", "created_at", "expires_at")


class PersonAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "nickname", "email", "updated_at")
    search_fields = ("first_name", "last_name", "nickname", "email")
    ordering = (
        "first_name",
        "last_name",
        "nickname",
        "email",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")


class LinkShortenerAdmin(admin.ModelAdmin):
    list_display = ("url", "slug", "comment", "counter", "created_at")
    search_fields = ("url", "slug", "comment")
    ordering = (
        "url",
        "slug",
        "comment",
        "counter",
        "created_at",
    )
    readonly_fields = ("counter", "created_at", "updated_at", "slug")


admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(Exhibitor)
admin.site.register(MagicLink, MagicLinkAdmin)
admin.site.register(Organisation)
admin.site.register(Person, PersonAdmin)
admin.site.register(Sponsoring)
admin.site.register(Type)
admin.site.register(LinkShortener, LinkShortenerAdmin)
