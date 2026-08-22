from __future__ import annotations

from django.contrib import admin

from rockon.library.custom_admin import CustomAdminModel
from rockon.news.models import NewsPost
from rockon.news.services.rendering import render_markdown_to_html


@admin.register(NewsPost)
class NewsPostAdmin(CustomAdminModel):
    list_display = ('title', 'status', 'event', 'publish_at', 'author')
    list_filter = ('status', 'event')
    search_fields = ('title', 'body_markdown')
    readonly_fields = CustomAdminModel.readonly_fields + ('body_html',)

    def save_model(self, request, obj, form, change):
        obj.body_html = render_markdown_to_html(obj.body_markdown)
        super().save_model(request, obj, form, change)
