from __future__ import annotations

import json
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.timezone import make_aware

from crm.models import MagicLink


def request_magic_link(request):
    try:
        body = json.loads(request.body)
        user = User.objects.get(
            email=body.get("contact_email"), last_name=body.get("user_last_name")
        )
        MagicLink.create_and_send(user, make_aware(datetime.now() + timedelta(weeks=4)))

    except User.DoesNotExist:
        pass

    return JsonResponse(
        {"status": "ok", "message": "Magic link sent if mail and last_name match"}
    )
