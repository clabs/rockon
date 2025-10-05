from __future__ import annotations

import json
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.timezone import make_aware

from rockon.base.models import MagicLink


def request_magic_link(request):
    try:
        body = json.loads(request.body)
        email = body.get('email')
        if not email:
            return JsonResponse(
                {'status': 'error', 'message': 'Email is required.'}, status=400
            )
        user = User.objects.get(email=email.lower())
        MagicLink.create_and_send(user, make_aware(datetime.now() + timedelta(weeks=4)))

    except User.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'User not found.'}, status=404
        )

    return JsonResponse(
        {'status': 'ok', 'message': 'Magic link sent if mail matches a user.'}
    )
