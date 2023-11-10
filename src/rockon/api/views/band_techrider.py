from __future__ import annotations

import json

from django.http import JsonResponse

from rockon.bands.models import Band


def band_techrider(request, slug):
    try:
        band = Band.objects.get(slug=slug)
        body = json.loads(request.body)
        body.pop("csrfmiddlewaretoken", None)
    except Band.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Band does not exist."}, status=404
        )
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON."}, status=400)

    band.techrider = body
    band.save()

    return JsonResponse({"status": "ok"})
