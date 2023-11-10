from __future__ import annotations

from rockon.library.custom_admin import CustomAdminModel, admin

from .models import Asset, Attendance, Exhibitor, ExhibitorAsset, ExhibitorAttendance


class ExhibitorAssetAdmin(CustomAdminModel):
    list_display = ("exhibitor", "asset", "count")
    list_filter = ("exhibitor", "asset")
    search_fields = ("exhibitor", "asset")


class ExhibitorAttendanceAdmin(CustomAdminModel):
    list_display = ("exhibitor", "day", "count")
    list_filter = ("day",)
    search_fields = ("exhibitor", "day")


class ExhibitorAdmin(CustomAdminModel):
    list_display = ("organisation", "event")
    list_filter = ("event",)
    search_fields = ("organisation", "event")


class AssetAdmin(CustomAdminModel):
    list_display = ("name", "is_bool", "description")
    search_fields = ("name", "is_bool", "description")


admin.site.register(Exhibitor, ExhibitorAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Attendance)
admin.site.register(ExhibitorAsset, ExhibitorAssetAdmin)
admin.site.register(ExhibitorAttendance, ExhibitorAttendanceAdmin)
