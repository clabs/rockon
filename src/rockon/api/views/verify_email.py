from __future__ import annotations

import json

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core import exceptions
from django.http import JsonResponse
from django.urls import reverse

from rockon.base.models import EmailVerification


def verify_email(request):
    try:
        token = json.loads(request.body).get("token")
        verification = EmailVerification.objects.get(token=token)
        if not verification.is_active:
            return JsonResponse({"status": "token_spent"}, status=201)
        user = User.objects.get(id=verification.user.id)
        user.profile.email_is_verified = True
        if verification.new_email:
            user.email = verification.new_email
            user.username = verification.new_email
        user.save()
        verification.is_active = False
        verification.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return JsonResponse({"status": "verified", "next": reverse("base:account")})
    except (
        EmailVerification.DoesNotExist,
        User.DoesNotExist,
        exceptions.ValidationError,
    ):
        return JsonResponse({"status": "error"}, status=400)
