from __future__ import annotations

from django.db import IntegrityError, transaction

from rockon.bands.models import Band, BandMedia, BandProfile, MediaType
from rockon.base.models import Event

# Identity data that carries over from a profile's previous bid. Year-specific
# data (cover letter, songs, track, techrider, status) always starts fresh.
_PREFILL_FIELDS = (
    'name',
    'genre',
    'federal_state',
    'is_flinta',
    'is_coverband',
    'are_students',
)
_PREFILL_MEDIA_TYPES = (
    MediaType.LINK,
    MediaType.WEB,
    MediaType.LOGO,
    MediaType.PRESS_PHOTO,
)


def start_bid(user, event: Event) -> tuple[Band, bool]:
    """Return the user's bid for `event`, creating it if needed.

    Returns (band, created).
    """
    existing = Band.objects.filter(contact=user, event=event).first()
    if existing:
        return existing, False

    try:
        return _create_bid(user, event), True
    except IntegrityError:
        # Concurrent request for the same profile and event won the race.
        band = Band.objects.filter(contact=user, event=event).first()
        if band is None:
            raise
        return band, False


def _create_bid(user, event: Event) -> Band:
    with transaction.atomic():
        profile = user.band_profiles.order_by('-created_at').first()
        if profile is None:
            profile = BandProfile.objects.create(owner=user)

        previous = profile.latest_bid()
        band = Band(
            event=event,
            contact=user,
            profile=profile,
            repeated=previous is not None,
        )
        if previous:
            for field in _PREFILL_FIELDS:
                setattr(band, field, getattr(previous, field))
        band.save()

        if previous:
            _copy_media(previous, band)
            # Media counts toward bid_complete, so re-evaluate after copying.
            band.save()

    return band


def _copy_media(source: Band, target: Band) -> None:
    # Copies reference the same stored files; nothing deletes files on media delete.
    BandMedia.objects.bulk_create(
        [
            BandMedia(
                band=target,
                media_type=media.media_type,
                url=media.url,
                file=media.file.name or None,
                encoded_file=media.encoded_file.name or None,
                thumbnail=media.thumbnail.name or None,
                file_name_original=media.file_name_original,
                encode_status=media.encode_status,
            )
            for media in source.media.filter(media_type__in=_PREFILL_MEDIA_TYPES)
        ]
    )


def sync_profile_name(band: Band) -> None:
    """Keep the profile name in step with the band's latest bid."""
    if not band.profile_id or not band.name:
        return
    if band.profile.latest_bid() != band:
        return
    BandProfile.objects.filter(id=band.profile_id).update(name=band.name)
