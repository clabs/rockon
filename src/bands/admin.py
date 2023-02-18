from __future__ import annotations

from django.contrib import admin

from .models import Band, BandMember, Stage, TimeSlot

admin.site.register(Band)
admin.site.register(BandMember)
admin.site.register(Stage)
admin.site.register(TimeSlot)
