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
from bblegacy.models import Bid, Media, Track, User, Vote


@csrf_exempt
@require_http_methods(["GET", "POST"])
def bid_create(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        try:
            new_bid = Bid.create_from_json(body)
            new_bid.send_welcome_mail()
        except Exception:
            return JsonResponse({"message": "Something went wrong"}, status=400)

        return JsonResponse({"bids": model_to_dict(new_bid)}, status=201)

    return JsonResponse({"message": "Method not yet implemented"}, status=405)


@csrf_exempt
@require_http_methods(["GET", "PUT", "POST"])
@bearer_token_required
def bid_handler(request, bid_id: str = None):
    if request.method == "GET":
        if not test_bearer_token(request.headers.get("Authorization"), role="crew"):
            return JsonResponse({"message": "Unauthorized"}, status=401)
        bids = Bid.objects.all()
        if request.GET.get("track"):
            bids = bids.filter(track=request.GET.get("track"))

        media = Media.objects.filter(bid__in=bids)
        votes = Vote.objects.filter(bid__in=bids)
        users = User.objects.all()

        response = {}
        response["media"] = [model_to_dict(media) for media in media]
        response["votes"] = [model_to_dict(vote) for vote in votes]
        response["users"] = [model_to_dict(user) for user in users]
        response["tracks"] = [model_to_dict(bid.track) for bid in bids if bid.track]
        response["bids"] = [bid.to_json() for bid in bids]

        return JsonResponse(response, status=200)

    if request.method == "PUT":
        if not test_bearer_token(request.headers.get("Authorization"), role="admin"):
            return JsonResponse({"message": "Unauthorized"}, status=401)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        try:
            bid = Bid.objects.get(id=bid_id)
            bid = bid.update_from_json(body)
            return JsonResponse({"bids": model_to_dict(bid)}, status=200)
        except Exception:
            return JsonResponse({"message": "Something went wrong"}, status=400)
