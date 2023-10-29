from __future__ import annotations

from django.forms import model_to_dict
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bblegacy.models import Region


@require_http_methods(["GET"])
def region_list(request):
    regions = Region.objects.all().values("name", "id", "created")
    data = {
        "regions": list(regions),
    }
    return JsonResponse(data)


def get_region(request, region_id):
    try:
        region = Region.objects.get(id=region_id)
    except Region.DoesNotExist:
        return JsonResponse({"message": "Region not found"}, status=404)

    return JsonResponse({"region": model_to_dict(region)}, status=200)
