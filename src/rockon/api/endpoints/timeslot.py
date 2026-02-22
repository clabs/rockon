from __future__ import annotations

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.timeslot import TimeSlotOut, TimeSlotPatchIn, TimeSlotPatchOut
from rockon.bands.models import Band, TimeSlot

timeslotRouter = Router()


def _check_booking(request):
    return request.user.groups.filter(name='booking').exists()


def _serialize_timeslot(ts):
    return {
        'id': str(ts.id),
        'stage_id': str(ts.stage_id),
        'stage_name': ts.stage.name,
        'day': ts.day.day.isoformat(),
        'day_label': ts.day.day.strftime('%a %d.%m.'),
        'start': ts.start.strftime('%H:%M'),
        'end': ts.end.strftime('%H:%M'),
        'band_id': str(ts.band_id) if ts.band_id else None,
        'band_name': ts.band.name if ts.band else None,
        'band_guid': ts.band.guid if ts.band else None,
        'band_genre': ts.band.genre or '' if ts.band else None,
        'band_track': ts.band.track.name if ts.band and ts.band.track else None,
    }


@timeslotRouter.get(
    '/', response=list[TimeSlotOut], url_name='timeslot_list', auth=django_auth
)
def list_timeslots(request, event: str | None = None):
    if not _check_booking(request):
        return 403, []
    qs = TimeSlot.objects.select_related('stage', 'day', 'band__track').order_by(
        'day__day', 'start'
    )
    if event:
        qs = qs.filter(stage__event__slug=event)
    return [_serialize_timeslot(ts) for ts in qs]


@timeslotRouter.patch(
    '/{timeslot_id}/',
    response=TimeSlotPatchOut,
    url_name='timeslot_patch',
    auth=django_auth,
)
def patch_timeslot(request, timeslot_id: str, data: TimeSlotPatchIn):
    if not _check_booking(request):
        return 403, None
    ts = get_object_or_404(
        TimeSlot.objects.select_related('band__track'), id=timeslot_id
    )

    if data.band_id is not None:
        band = get_object_or_404(Band, id=data.band_id, bid_status='lineup')
        # If this band is already in another slot, clear that slot first
        TimeSlot.objects.filter(band=band).exclude(id=ts.id).update(band=None)
        ts.band = band
    else:
        ts.band = None

    ts.save()
    ts.refresh_from_db()
    ts = TimeSlot.objects.select_related('band__track').get(id=ts.id)
    return {
        'id': str(ts.id),
        'band_id': str(ts.band_id) if ts.band_id else None,
        'band_name': ts.band.name if ts.band else None,
        'band_guid': ts.band.guid if ts.band else None,
        'band_genre': ts.band.genre or '' if ts.band else None,
        'band_track': ts.band.track.name if ts.band and ts.band.track else None,
        'updated_at': ts.updated_at,
    }
