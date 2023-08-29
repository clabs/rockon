from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from crm.models import EmailVerification


@login_required
@require_http_methods(["POST"])
def update_user_email(request):
    user = request.user

    body = json.loads(request.body)

    if not body.get("changeEmailNew", True) == body.get("changeEmailRepeat", False):
        return JsonResponse({"status": "error", "message": "E-Mail is required"})

    EmailVerification.objects.filter(user=user).delete()
    EmailVerification.create_and_send(user=user, new_email=body["changeEmailNew"])

    return JsonResponse({"status": "ok", "message": "E-Mail updated"})
