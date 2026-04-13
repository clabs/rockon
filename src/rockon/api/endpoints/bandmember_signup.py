from __future__ import annotations

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import transaction
from ninja import Router

from rockon.api.schemas.bandmember import BandMemberSignupIn
from rockon.api.schemas.status import StatusOut
from rockon.bands.models import Band, BandMember

bandmemberSignupRouter = Router()


@bandmemberSignupRouter.post(
    '/',
    response={200: StatusOut, 404: StatusOut},
    url_name='bandmember_signup',
)
def bandmember_signup(request, data: BandMemberSignupIn):
    """Register band members for a band."""
    try:
        band = Band.objects.get(id=data.band)
    except Band.DoesNotExist:
        return 404, {'status': 'error', 'message': 'Band does not exist.'}

    with transaction.atomic():
        emails = [p.email.lower() for p in data.persons]
        existing_users = {u.email: u for u in User.objects.filter(email__in=emails)}

        new_members = []
        for person in data.persons:
            if BandMember.objects.filter(band=band).count() >= 10:
                break

            email = person.email.lower()

            if email in existing_users:
                # Email already taken — create an alias to avoid overwriting data
                new_mail_alias = f'band_{band.slug}_{uuid4().hex}@rockon.dev'
                user = User.objects.create(
                    username=new_mail_alias,
                    email=new_mail_alias,
                    first_name=person.first_name,
                    last_name=person.last_name,
                )
                user.profile.contact_mail = email
            else:
                user = User.objects.create(
                    username=email,
                    email=email,
                    first_name=person.first_name,
                    last_name=person.last_name,
                )

            user.profile.address = person.address
            user.profile.address_housenumber = person.housenumber
            user.profile.zip_code = person.zip_code
            user.profile.place = person.place
            user.save()

            new_members.append(
                BandMember(
                    band=band,
                    nutrition=person.nutrition,
                    position=person.position,
                    user=user,
                )
            )

        BandMember.objects.bulk_create(new_members)

    return 200, {'status': 'ok', 'message': 'Entries done.'}
