from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.band import (
    BandDetailOut,
    BandListOut,
    BandPatchIn,
    BandPatchOut,
)
from rockon.bands.models import Band, BandMedia
from rockon.library.mailer import get_admin_url, send_mail_async

logger = logging.getLogger(__name__)

bandRouter = Router()

# BandPatchIn fields that belong to the applicant's bid form, as opposed to
# booking-only fields (bid_status, track) — used to avoid notifying booking
# about its own bid_status/track edits.
_BID_FORM_FIELDS = (
    'name',
    'genre',
    'federal_state',
    'cover_letter',
    'are_students',
    'mean_age_under_27',
    'average_age',
    'is_coverband',
    'is_flinta',
)

# Fields needed for the list serializer — everything else is deferred.
_BAND_LIST_FIELDS = (
    'id',
    'guid',
    'name',
    'track_id',
    'bid_status',
    'federal_state',
    'are_students',
    'mean_age_under_27',
    'is_coverband',
    'is_flinta',
    'bid_complete',
    'created_at',
    'updated_at',
)

# Media fields needed in the list view.
_MEDIA_LIST_FIELDS = (
    'id',
    'band_id',
    'media_type',
    'url',
    'file',
    'encoded_file',
    'file_name_original',
    'thumbnail',
)

# Only media types used in the list view.
_MEDIA_LIST_TYPES = ('audio', 'press_photo', 'logo')


def _serialize_media(media):
    """Serialize a BandMedia instance to a dict."""
    return {
        'id': str(media.id),
        'media_type': media.media_type,
        'url': media.url,
        'file': media.file.url if media.file else None,
        'encoded_file': media.encoded_file.url if media.encoded_file else None,
        'file_name_original': media.file_name_original,
        'thumbnail': media.thumbnail.url if media.thumbnail else None,
        'band': str(media.band_id),
    }


def _serialize_media_file(media):
    """Serialize a BandMedia instance to file-only fields."""
    if media is None:
        return None
    return {
        'file': media.file.url if media.file else None,
        'encoded_file': media.encoded_file.url if media.encoded_file else None,
    }


def _serialize_band_list(band):
    """Serialize a Band for the list response.

    Assumes band.media is prefetched — filters in Python to avoid N+1 queries.
    """
    # Use the prefetched media cache instead of hitting the DB
    media = band.media.all()
    songs = [_serialize_media(m) for m in media if m.media_type == 'audio']
    press_photo = next((m for m in media if m.media_type == 'press_photo'), None)
    logo = next((m for m in media if m.media_type == 'logo'), None)

    return {
        'id': str(band.id),
        'guid': band.guid,
        'name': band.name,
        'track': str(band.track_id) if band.track_id else None,
        'songs': songs,
        'bid_status': band.bid_status,
        'federal_state': band.federal_state,
        'are_students': band.are_students,
        'mean_age_under_27': band.mean_age_under_27,
        'is_coverband': band.is_coverband,
        'is_flinta': band.is_flinta,
        'bid_complete': band.bid_complete,
        'press_photo': _serialize_media_file(press_photo),
        'logo': _serialize_media_file(logo),
        'created_at': band.created_at,
        'updated_at': band.updated_at,
    }


def _serialize_band_detail(band):
    """Serialize a Band for the detail response."""
    contact = band.contact
    contact_data = None
    if contact:
        contact_data = {
            'id': contact.id,
            'username': contact.username,
            'email': contact.email,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
        }

    # Use prefetched media cache to avoid N+1 queries
    media = list(band.media.all())
    songs = [_serialize_media(m) for m in media if m.media_type == 'audio']
    links = [_serialize_media(m) for m in media if m.media_type == 'link']
    web_links = [_serialize_media(m) for m in media if m.media_type == 'web']
    documents = [_serialize_media(m) for m in media if m.media_type == 'document']
    press_photo = next((m for m in media if m.media_type == 'press_photo'), None)
    logo = next((m for m in media if m.media_type == 'logo'), None)

    return {
        'id': str(band.id),
        'guid': band.guid,
        'slug': band.slug,
        'name': band.name,
        'event': str(band.event_id),
        'track': str(band.track_id) if band.track_id else None,
        'bid_status': band.bid_status,
        'federal_state': band.federal_state,
        'are_students': band.are_students,
        'mean_age_under_27': band.mean_age_under_27,
        'average_age': band.average_age,
        'is_coverband': band.is_coverband,
        'is_flinta': band.is_flinta,
        'repeated': band.repeated,
        'bid_complete': band.bid_complete,
        'genre': band.genre,
        'cover_letter': band.cover_letter,
        'contact': contact_data,
        'songs': songs,
        'links': links,
        'web_links': web_links,
        'documents': documents,
        'press_photo': _serialize_media_file(press_photo),
        'logo': _serialize_media_file(logo),
        'created_at': band.created_at,
        'updated_at': band.updated_at,
    }


@bandRouter.get(
    '/',
    response=list[BandListOut],
    url_name='band_list',
    auth=django_auth,
)
def list_bands(request, event: str | None = None):
    """List all bands, optionally filtered by event slug."""
    media_qs = BandMedia.objects.filter(
        media_type__in=_MEDIA_LIST_TYPES,
    ).only(*_MEDIA_LIST_FIELDS)

    queryset = Band.objects.only(*_BAND_LIST_FIELDS).prefetch_related(
        Prefetch('media', queryset=media_qs)
    )
    if event:
        queryset = queryset.filter(event__slug=event)
    return [_serialize_band_list(band) for band in queryset]


@bandRouter.get(
    '/{band_id}',
    response=BandDetailOut,
    url_name='band_detail',
    auth=django_auth,
)
def get_band(request, band_id: str):
    """Get full details for a single band."""
    band = get_object_or_404(
        Band.objects.select_related('track', 'contact').prefetch_related('media'),
        id=band_id,
    )
    if not request.user.is_staff and not request.user.bands.filter(id=band.id).exists():
        return HttpResponse(status=403)
    return _serialize_band_detail(band)


@bandRouter.patch(
    '/{band_id}',
    response={200: BandPatchOut, 403: None},
    url_name='band_patch',
    auth=django_auth,
)
def patch_band(request, band_id: str, data: BandPatchIn):
    """Update band fields. bid_status requires the 'booking' group."""
    band = get_object_or_404(Band, id=band_id)

    # Permission: must be admin, owner, or crew
    user = request.user
    is_admin = user.is_staff
    is_owner = band.contact == user
    is_crew = user.groups.filter(name='crew').exists()

    if not (is_admin or is_owner or is_crew):
        return 403, None

    had_complete = band.bid_complete
    bid_fields_touched = any(
        getattr(data, field) is not None for field in _BID_FORM_FIELDS
    )

    # bid_status requires 'booking' group
    if data.bid_status is not None:
        if not user.groups.filter(name='booking').exists():
            return 403, None
        band.bid_status = data.bid_status

    if data.track is not None:
        band.track_id = data.track  # type: ignore[attr-defined]

    # Bid form fields
    if data.name is not None:
        band.name = data.name
    if data.genre is not None:
        band.genre = data.genre
    if data.federal_state is not None:
        band.federal_state = data.federal_state
    if data.cover_letter is not None:
        band.cover_letter = data.cover_letter
    if data.are_students is not None:
        band.are_students = data.are_students
    if data.mean_age_under_27 is not None:
        band.mean_age_under_27 = data.mean_age_under_27
    if data.average_age is not None:
        band.average_age = data.average_age
    if data.is_coverband is not None:
        band.is_coverband = data.is_coverband
    if data.is_flinta is not None:
        band.is_flinta = data.is_flinta

    band.save()

    if bid_fields_touched and band.bid_complete:
        _send_booking_notification(
            band, notification_type='updated' if had_complete else 'created'
        )

    return {
        'id': str(band.id),
        'track': str(band.track.id) if band.track else None,
        'bid_status': band.bid_status,
        'bid_complete': band.bid_complete,
        'updated_at': band.updated_at,
    }


def _send_booking_notification(band, notification_type: str = 'created'):
    """Notify booking about a new or updated complete band bid. Failures are logged, never block the response."""
    try:
        recipients = list(
            Group.objects.get(name='booking').user_set.values_list('email', flat=True)
        )
        if not recipients:
            return

        admin_url = get_admin_url(band)
        is_update = notification_type == 'updated'
        intro_text = (
            f'eine bestehende Bandbewerbung bei {band.event.name} wurde aktualisiert.'
            if is_update
            else f'es gibt eine neue vollständige Bandbewerbung bei {band.event.name}.'
        )
        subject = (
            f'{settings.EMAIL_SUBJECT_PREFIX} Bandbewerbung aktualisiert'
            if is_update
            else f'{settings.EMAIL_SUBJECT_PREFIX} Neue Bandbewerbung'
        )

        template = loader.get_template('mail/band_bid.html')
        extra_context = {
            'event_name': band.event.name,
            'band_name': band.name,
            'genre': band.genre,
            'admin_url': admin_url,
            'is_update': is_update,
        }

        message = f'Hallo Booking,\n{intro_text}\nBand: {band.name}'
        if band.genre:
            message += f'\nGenre: {band.genre}'
        message += f'\n\nIm Admin ansehen: {admin_url}'

        send_mail_async(
            subject=subject,
            message=message,
            recipient_list=recipients,
            html_message=template.render(extra_context),
        )
    except Group.DoesNotExist:
        pass  # No booking group configured
    except Exception:
        logger.exception('Error sending band bid notification')
