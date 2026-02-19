from __future__ import annotations

from rockon.library.custom_admin import CustomAdminModel, admin
from .models import Asset, Attendance, Exhibitor, ExhibitorAsset, ExhibitorAttendance


@admin.register(ExhibitorAsset)
class ExhibitorAssetAdmin(CustomAdminModel):
    list_display = ('exhibitor', 'asset', 'count')
    list_filter = ('exhibitor', 'asset', 'exhibitor__event')
    search_fields = ('exhibitor', 'asset')


@admin.register(ExhibitorAttendance)
class ExhibitorAttendanceAdmin(CustomAdminModel):
    list_display = ('exhibitor', 'day', 'count', 'day__event')
    list_filter = ('day', 'day__event__name')
    search_fields = ('exhibitor', 'day')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('day__event', 'exhibitor')


class ExhibitorAssetInline(admin.TabularInline):
    model = ExhibitorAsset
    extra = 0
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Exhibitor)
class ExhibitorAdmin(CustomAdminModel):
    inlines = (ExhibitorAssetInline,)
    list_display = ('organisation', 'event', 'state', 'website', 'created_at')
    list_filter = ('event', 'state')
    search_fields = ('organisation', 'event')
    readonly_fields = ('logo_preview',)

    @admin.display(description='Logo Vorschau')
    def logo_preview(self, obj):
        if obj.logo:
            from django.utils.html import format_html

            return format_html(
                '<img src="{}" style="max-height: 100px;" />', obj.logo.url
            )
        return '-'


@admin.register(Asset)
class AssetAdmin(CustomAdminModel):
    list_display = ('name', 'is_bool', 'description')
    search_fields = ('name', 'is_bool', 'description')


@admin.register(Attendance)
class AttendanceAdmin(CustomAdminModel):
    list_display = (
        'day',
        'event',
    )
    list_filter = ('event',)
