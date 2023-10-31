from __future__ import annotations

import json

from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bblegacy.bearer_token_auth import (
    bearer_token_admin,
    bearer_token_crew,
    bearer_token_required,
    test_bearer_token,
)
from bblegacy.models import Bid, User, Vote


@csrf_exempt
@bearer_token_crew
@require_http_methods(["POST", "GET", "DELETE", "PUT"])
def vote_handler(request, vote_id: str = None):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        user = User.objects.get(id=body["user"])
        bid = Bid.objects.get(id=body["bid"])
        vote = Vote.objects.update_or_create(
            bid=bid, user=user, defaults={"rating": body["rating"]}
        )
        return JsonResponse({"votes": model_to_dict(vote[0])}, status=201)

    if request.method == "PUT":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        vote = Vote.objects.get(id=vote_id)
        vote.rating = body["rating"]
        vote.save()
        return JsonResponse({"votes": model_to_dict(vote)}, status=201)
