from __future__ import annotations

import json

from django.forms import model_to_dict
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bblegacy.models import Bid


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
@require_http_methods(["GET", "PUT"])
def bid_handler(request, id):
    try:
        bid = Bid.objects.get(id=id)
    except Bid.DoesNotExist:
        return JsonResponse({"message": "Bid not found"}, status=404)

    if request.method == "GET":
        _media = [model_to_dict(media) for media in bid.media.all()]

        return JsonResponse({"bids": model_to_dict(bid), "media": _media}, status=200)

    if request.method == "PUT":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        try:
            bid = Bid.objects.get(id=id)
            bid.update_from_json(body)
            return JsonResponse({"message": "Bid updated"}, status=200)
        except Exception:
            return JsonResponse({"message": "Something went wrong"}, status=400)
