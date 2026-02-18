from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile
from ninja.security import django_auth

from rockon.api.schemas.band_media import BandMediaOut
from rockon.bands.models import Band, BandMedia

bandMediaRouter = Router()


def _serialize_media(media: BandMedia) -> dict:
    return {
        'id': str(media.id),
        'band': str(media.band_id),
        'media_type': media.media_type,
        'url': media.url,
        'file': media.file.url if media.file else None,
        'encoded_file': media.encoded_file.url if media.encoded_file else None,
        'file_name_original': media.file_name_original,
        'thumbnail': media.thumbnail.url if media.thumbnail else None,
        'created_at': media.created_at,
        'updated_at': media.updated_at,
    }


@bandMediaRouter.get(
    '/',
    response=list[BandMediaOut],
    url_name='band_media_list',
    auth=django_auth,
)
def list_media(request, band_id: str | None = None):
    """List media, optionally filtered by band_id."""
    queryset = BandMedia.objects.all()
    if band_id:
        queryset = queryset.filter(band__id=band_id)
    if not request.user.is_staff:
        user_bands = request.user.bands.values_list('id', flat=True)
        queryset = queryset.filter(band__id__in=user_bands)
    return [_serialize_media(m) for m in queryset]


@bandMediaRouter.post(
    '/upload/',
    response={201: BandMediaOut},
    url_name='band_media_upload',
    auth=django_auth,
)
def upload_media(
    request,
    file: UploadedFile | None = File(None),
):
    """Create a media entry with optional file upload (multipart) or URL (JSON)."""
    import json

    # Multipart form data (file uploads) — fields are in request.POST
    band = request.POST.get('band')
    media_type = request.POST.get('media_type', 'unknown')
    url = request.POST.get('url')

    # JSON body (URL additions) — POST is empty, stream not yet consumed
    if not band:
        try:
            body = json.loads(request.body)
            band = body.get('band')
            media_type = body.get('media_type', 'unknown')
            url = body.get('url')
        except json.JSONDecodeError, UnicodeDecodeError, Exception:
            pass

    if not band:
        return HttpResponse(status=400, content='band is required')

    band_obj = get_object_or_404(Band, id=band)
    user = request.user
    if not user.bands.filter(id=band_obj.id).exists() and not user.is_staff:
        return HttpResponse(
            status=403, content='You can only upload media for your own band.'
        )

    media = BandMedia(
        band=band_obj,
        media_type=media_type or 'unknown',
    )
    if url:
        media.url = url
    if file:
        media.file = file
    media.save()

    if file:
        media.encode_file()

    return 201, _serialize_media(media)


@bandMediaRouter.delete(
    '/{media_id}/',
    response={204: None},
    url_name='band_media_delete',
    auth=django_auth,
)
def delete_media(request, media_id: str):
    """Delete a media entry."""
    media = get_object_or_404(BandMedia, id=media_id)
    user = request.user
    if not user.is_staff:
        if not user.bands.filter(id=media.band_id).exists():
            return HttpResponse(
                status=403, content='You can only delete media for your own band.'
            )
    media.delete()
    return 204, None
