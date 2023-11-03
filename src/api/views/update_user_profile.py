from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["POST"])
def update_user_profile(request):
    user = request.user

    body = json.loads(request.body)

    user.first_name = body["first_name"]
    user.last_name = body["last_name"]
    # FIXME: logic for changing email, needs verification mail
    user.save()

    profile = user.profile

    _birhtday = None
    if body["user_birthday"]:
        _birhtday = body["user_birthday"]

    profile.nick_name = body["nick_name"]
    profile.phone = body["phone"]
    profile.address = body["address"]
    profile.address_extension = body["address_extension"]
    profile.address_housenumber = body["address_housenumber"]
    profile.zip_code = body["zip_code"]
    profile.place = body["place"]
    profile.birthday = _birhtday

    profile.save()

    return JsonResponse({"status": "ok", "message": "Profile updated"})
