from __future__ import annotations

from library.custom_admin import CustomAdminModel, admin

from .models import LinkShortener


class LinkShortenerAdmin(CustomAdminModel):
    list_display = ("url", "slug", "comment", "counter", "created_at")
    search_fields = ("url", "slug", "comment")
    ordering = (
        "url",
        "slug",
        "comment",
        "counter",
        "created_at",
    )
    readonly_fields = ("counter",)


admin.site.register(LinkShortener, LinkShortenerAdmin)
