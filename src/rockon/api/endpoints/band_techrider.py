from __future__ import annotations

from typing import Any

from ninja import Router

from rockon.api.schemas.status import StatusOut
from rockon.bands.models import Band

bandTechriderRouter = Router()


@bandTechriderRouter.post(
    '/{slug}/',
    response={200: StatusOut, 404: StatusOut},
    url_name='band_techrider',
)
def band_techrider(request, slug: str, data: dict[str, Any]):
    """Save techrider data for a band."""
    try:
        band = Band.objects.get(slug=slug)
    except Band.DoesNotExist:
        return 404, {'status': 'error', 'message': 'Band does not exist.'}

    data.pop('csrfmiddlewaretoken', None)
    band.techrider = data
    band.save()

    return 200, {'status': 'ok'}
