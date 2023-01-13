from __future__ import annotations

from django.contrib import admin

from .models import LinkShortener


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
    readonly_fields = ("created_at", "updated_at")


admin.site.register(LinkShortener, LinkShortenerAdmin)
