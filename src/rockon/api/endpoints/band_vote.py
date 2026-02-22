from __future__ import annotations

from django.db import transaction
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.band_vote import BandVoteIn, BandVoteOut
from rockon.bands.models import Band, BandVote

bandVote = Router()


@bandVote.get(
    '/{band_id}',
    response={200: BandVoteOut, 204: None},
    url_name='band_vote_detail',
    auth=django_auth,
)
def get_vote(request, band_id: str):
    """Get the current user's vote for a specific band."""
    vote = BandVote.objects.filter(user=request.user, band__id=band_id).first()
    if vote is None:
        return 204, None
    return 200, {
        'band': str(vote.band_id),
        'user': vote.user_id,
        'vote': vote.vote,
    }


@bandVote.patch(
    '',
    response={201: None, 204: None, 404: None},
    url_name='band_vote_submit',
    auth=django_auth,
)
def submit_vote(request, data: BandVoteIn):
    """Create or update a vote. A vote of -1 deletes the existing vote (abstain)."""
    try:
        band = Band.objects.select_related('event').get(id=data.band)
    except Band.DoesNotExist:
        return 404, None
    user = request.user
    with transaction.atomic():
        if data.vote == -1:
            BandVote.objects.filter(band=band, user=user).delete()
            return 204, None
        BandVote.objects.update_or_create(
            band=band, user=user, defaults={'vote': data.vote, 'event': band.event}
        )
    return 201, None
