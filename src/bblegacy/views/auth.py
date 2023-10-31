from __future__ import annotations

import hashlib

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bblegacy.models import Token, User


@csrf_exempt
@require_http_methods(["POST"])
def auth_local(request):
    form_data = request.POST
    try:
        password = hashlib.sha256(form_data.get("password").encode()).hexdigest()
        user = User.objects.get(email=form_data.get("email"), password=password)

        token = Token.create(user)

        response = {
            "token": {
                "user": user.id,
                "id": token.id,
                "timestamp": token.timestamp.timestamp(),
            }
        }

        return JsonResponse(response, status=200)

    except User.DoesNotExist:
        pass

    return JsonResponse({"error": "user or password not correct"}, status=400)
