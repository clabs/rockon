from __future__ import annotations

from django.contrib import admin

# WONTFIX: stop black and isort from messing up the imports
# fmt: off
from .models import Asset, Attendance, Exhibitor, ExhibitorAsset, ExhibitorAttendance

# fmt: on


class ExhibitorAssetAdmin(admin.ModelAdmin):
    list_display = ("exhibitor", "asset", "count")
    list_filter = ("exhibitor", "asset")
    search_fields = ("exhibitor", "asset")


admin.site.register(Exhibitor)
admin.site.register(Asset)
admin.site.register(Attendance)
admin.site.register(ExhibitorAsset, ExhibitorAssetAdmin)
admin.site.register(ExhibitorAttendance)
