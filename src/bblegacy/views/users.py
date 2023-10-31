from __future__ import annotations

import json

from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bblegacy.bearer_token_auth import (
    bearer_token_admin,
    bearer_token_required,
    test_bearer_token,
)
from bblegacy.models import Token, User


@csrf_exempt
@bearer_token_required
@require_http_methods(["GET"])
def get_user(request, user_id):
    try:
        token = Token.objects.get(id=request.headers.get("Authorization").split(" ")[1])
        if not token.user.role == "admin" or not token.user.id == user_id:
            raise Token.DoesNotExist
    except Token.DoesNotExist:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        user = User.objects.get(id=user_id)

        return JsonResponse({"users": model_to_dict(user)}, status=200)

    except User.DoesNotExist:
        pass

    return JsonResponse({"error": "user not found"}, status=404)


@csrf_exempt
@bearer_token_required
@require_http_methods(["POST", "PUT", "GET"])
def user_handler(request, user_id: str = None):
    if request.method == "GET":
        if (
            not test_bearer_token(request.headers.get("Authorization"), role="admin")
            and not user_id
        ):
            return JsonResponse({"error": "Unauthorized"}, status=401)

        try:
            users = User.objects.all()
            if user_id:
                user = users.filter(id=user_id).first()
                _user = model_to_dict(user, exclude=["password"])
                return JsonResponse({"users": _user}, status=200)
            _users = [model_to_dict(user, exclude=["password"]) for user in users]
            return JsonResponse({"users": _users}, status=200)
        except Exception:
            return JsonResponse({"message": "Something went wrong"}, status=400)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)

    if request.method == "POST":
        if not test_bearer_token(request.headers.get("Authorization"), role="admin"):
            return JsonResponse({"error": "Unauthorized"}, status=401)

        try:
            user = User.create_from_json(body)
            _user = model_to_dict(user, exclude=["password"])
            return JsonResponse({"users": _user}, status=201)
        except Exception:
            return JsonResponse({"message": "Something went wrong"}, status=400)

    if request.method == "PUT":
        if not test_bearer_token(request.headers.get("Authorization"), role="admin"):
            return JsonResponse({"error": "Unauthorized"}, status=401)

        try:
            user = User.objects.get(id=user_id)
            user = user.update_from_json(body)
            _user = model_to_dict(user, exclude=["password"])
            return JsonResponse({"users": _user}, status=200)
        except Exception:
            return JsonResponse({"message": "Something went wrong"}, status=400)
