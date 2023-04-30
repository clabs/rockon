from __future__ import annotations

import json
from uuid import uuid4

from django.contrib.auth.models import User
from django.http import JsonResponse

from bands.models import Band, BandMember


def bandmember_signup(request):
    body = json.loads(request.body)
    try:
        band = Band.objects.get(id=body["band"])
    except Band.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Band does not exist."}, status=404
        )

    for person in body["persons"]:
        if BandMember.objects.filter(band=band).count() >= 10:
            break
        person_dict = {}
        for item in person:
            person_dict[item["name"]] = item["value"]
        try:
            user = User.objects.get(email=person_dict["email"])
            # if a user already exists, create a new mail alias
            # to prevent information being overwritten
            # because bands use their booking mail address for all members
            new_mail_alias = f"band_{band.slug}_{uuid4().hex}@rockon.dev"
            user = User.objects.create(
                username=new_mail_alias,
                email=new_mail_alias,
                first_name=person_dict["first_name"],
                last_name=person_dict["last_name"],
            )
            user.profile.contact_mail = person_dict["email"]
        except User.DoesNotExist:
            user = User.objects.create(
                username=person_dict["email"],
                email=person_dict["email"],
                first_name=person_dict["first_name"],
                last_name=person_dict["last_name"],
            )

        user.profile.address = person_dict["address"]
        user.profile.zip_code = person_dict["zip_code"]
        user.profile.place = person_dict["place"]

        user.save()

        band_member = BandMember(
            band=band,
            nutrition=person_dict["nutrition"],
            position=person_dict["position"],
            user=user,
        )

        band_member.save()

    return JsonResponse({"status": "ok", "message": "Entries done."}, status=200)
