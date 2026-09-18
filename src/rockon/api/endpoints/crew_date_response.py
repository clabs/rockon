from __future__ import annotations

from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.crew_date_response import (
    CrewDateResponseIn,
    CrewDateResponseOut,
)
from rockon.api.schemas.status import StatusOut
from rockon.crew.models import CrewDate, CrewDateResponse, CrewDateResponseStatus

crewDateResponse = Router()


@crewDateResponse.get(
    '/{crew_date_id}',
    response={200: CrewDateResponseOut, 204: None},
    url_name='crew_date_response_detail',
    auth=django_auth,
)
def get_response(request, crew_date_id: str):
    """Get the current user's RSVP status for a specific crew date."""
    response = CrewDateResponse.objects.filter(
        user=request.user, crew_date__id=crew_date_id
    ).first()
    if response is None:
        return 204, None
    return 200, {'crew_date': str(response.crew_date_id), 'status': response.status}


@crewDateResponse.patch(
    '',
    response={201: None, 400: StatusOut, 403: StatusOut, 404: StatusOut},
    url_name='crew_date_response_submit',
    auth=django_auth,
)
def submit_response(request, data: CrewDateResponseIn):
    """Create or update the current user's RSVP status for a crew date."""
    if data.status not in CrewDateResponseStatus.values:
        return 400, {'status': 'error', 'message': 'Invalid status'}
    try:
        crew_date = CrewDate.objects.select_related('crew').get(id=data.crew_date)
    except CrewDate.DoesNotExist:
        return 404, {'status': 'error', 'message': 'Crew date not found'}
    if not crew_date.crew.is_member(request.user):
        return 403, {'status': 'error', 'message': 'Not a confirmed crew member'}
    CrewDateResponse.objects.update_or_create(
        crew_date=crew_date, user=request.user, defaults={'status': data.status}
    )
    return 201, None
