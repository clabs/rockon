from __future__ import annotations

from library.custom_admin import CustomAdminModel, admin

from .models import Event, Task, Timeline

admin.site.register(Event)
admin.site.register(Task)
admin.site.register(Timeline)
