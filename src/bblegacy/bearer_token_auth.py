from __future__ import annotations

from functools import wraps

from django.http import JsonResponse

from bblegacy.models import Token


def test_bearer_token(auth_header, role: str = None) -> bool:
    if not auth_header or not auth_header.startswith("Bearer "):
        return False

    token = auth_header.split(" ")[1]
    try:
        _token = Token.objects.get(id=token)
        if role is None:
            return True
        if _token.user.role == "admin":
            return True
        if _token.user.role == role:
            return True
    except Token.DoesNotExist:
        return False

    return False


def bearer_token_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token_is_valid = test_bearer_token(auth_header)

        if not token_is_valid:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def bearer_token_crew(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token_is_valid = test_bearer_token(auth_header, role="crew")

        if not token_is_valid:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def bearer_token_admin(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token_is_valid = test_bearer_token(auth_header, role="admin")

        if not token_is_valid:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
