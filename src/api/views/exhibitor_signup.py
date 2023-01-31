from __future__ import annotations

import json

from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, JsonResponse

from crm.models import EmailVerification
from event.models import Event


def exhibitor_signup(request, slug):
    created_user = False
    # FIXME: refactor to Django forms to validate input and use Django's CSRF protection
    body = json.loads(request.body)

    event = Event.objects.get(slug=slug)

    try:
        user = User.objects.get(email=body["user_email"])
        return HttpResponseBadRequest("User already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=body["user_email"],
            email=body["user_email"],
            password=None,
            first_name=body["user_first_name"],
            last_name=body["user_last_name"],
        )

        user.save()

        # FIXME: need try create and catch IntegrityError

        user.profile.nick_name = body.get("user_nick_name")
        user.profile.phone = body.get("user_mobile")
        user.profile.address = body.get("user_address")
        user.profile.address_housenumber = body.get("user_address_housenumber")
        user.profile.address_extension = body.get("user_address_extension")
        user.profile.zip_code = body.get("user_zipcode")
        user.profile.place = body.get("user_place")

        EmailVerification.create_and_send(user=user)

        created_user = True

    user.events.add(event)
    user.save()

    if created_user:
        return JsonResponse({"status": "created", "message": "User created"})
    elif not created_user:
        return JsonResponse({"status": "exists", "message": "User already exists"})
    else:
        return JsonResponse(
            {"status": "error", "message": "Something went horribly wrong"}, status=500
        )
