from __future__ import annotations

from django.contrib import admin

from .models import Event, Task, Timeline

admin.site.register(Event)
admin.site.register(Task)
admin.site.register(Timeline)
