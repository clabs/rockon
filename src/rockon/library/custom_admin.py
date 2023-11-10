from __future__ import annotations

from django.contrib import admin


class CustomAdminModel(admin.ModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
        "id",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = self.readonly_fields + CustomAdminModel.readonly_fields
