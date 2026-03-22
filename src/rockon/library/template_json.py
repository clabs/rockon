from __future__ import annotations

import json

from django.utils.safestring import mark_safe


def template_json(data, *, ensure_ascii: bool = True):
    """Serialize data for template embedding as a safe JSON string."""
    return mark_safe(json.dumps(data, ensure_ascii=ensure_ascii))
