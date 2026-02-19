from __future__ import annotations

import json
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse

from rockon.bands.models import Band, BandMember


def bandmember_signup(request):
    body = json.loads(request.body)
    try:
        band = Band.objects.get(id=body['band'])
    except Band.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Band does not exist.'}, status=404
        )

    with transaction.atomic():
        # Pre-fetch existing users by email to avoid per-person queries
        persons = body['persons']
        person_dicts = []
        for person in persons:
            person_dict = {item['name']: item['value'] for item in person}
            person_dict['email'] = person_dict['email'].lower()
            person_dicts.append(person_dict)

        emails = [p['email'] for p in person_dicts]
        existing_users = {u.email: u for u in User.objects.filter(email__in=emails)}

        new_members = []
        for person_dict in person_dicts:
            if BandMember.objects.filter(band=band).count() >= 10:
                break

            if person_dict['email'] in existing_users:
                # Email already taken — create an alias to avoid overwriting data
                new_mail_alias = f'band_{band.slug}_{uuid4().hex}@rockon.dev'
                user = User.objects.create(
                    username=new_mail_alias,
                    email=new_mail_alias,
                    first_name=person_dict['first_name'],
                    last_name=person_dict['last_name'],
                )
                user.profile.contact_mail = person_dict['email']
            else:
                user = User.objects.create(
                    username=person_dict['email'],
                    email=person_dict['email'],
                    first_name=person_dict['first_name'],
                    last_name=person_dict['last_name'],
                )

            user.profile.address = person_dict['address']
            user.profile.address_housenumber = person_dict['housenumber']
            user.profile.zip_code = person_dict['zip_code']
            user.profile.place = person_dict['place']
            user.save()

            new_members.append(
                BandMember(
                    band=band,
                    nutrition=person_dict['nutrition'],
                    position=person_dict['position'],
                    user=user,
                )
            )

        BandMember.objects.bulk_create(new_members)

    return JsonResponse({'status': 'ok', 'message': 'Entries done.'}, status=200)
