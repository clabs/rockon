from __future__ import annotations

import json

from django.contrib.auth.models import User
from django.http import JsonResponse

from rockon.base.models import EmailVerification, Event, Organisation
from rockon.exhibitors.models import (
    Asset,
    Attendance,
    Exhibitor,
    ExhibitorAsset,
    ExhibitorAttendance,
)


def exhibitor_signup(request, slug):
    created_user = False
    # FIXME: refactor to Django forms to validate input and use Django's CSRF protection
    body_list = json.loads(request.body)
    body = {}
    for item in body_list:
        body[item["name"]] = item["value"]

    try:
        event = Event.objects.get(slug=slug)
    except Event.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Event not found"}, status=404
        )

    try:
        user = User.objects.get(email=body["user_email"])
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=body["user_email"],
            email=body["user_email"],
            password=None,
            first_name=body["user_first_name"],
            last_name=body["user_last_name"],
        )

        # Save is needed to create a profile for the user with the post_save signal
        user.save()

        # FIXME: need try create and catch IntegrityError
        user.profile.phone = body.get("user_phone")
        EmailVerification.create_and_send(user=user)

        created_user = True

    user.profile.events.add(event)
    user.save()

    try:
        organisation = Organisation.objects.get(org_name=body["organisation_name"])
    except Organisation.DoesNotExist:
        organisation = Organisation.objects.create(
            org_name=body["organisation_name"],
            org_address=body["organisation_address"],
            org_house_number=body["organisation_address_housenumber"],
            org_address_extension=body["organisation_address_extension"],
            org_zip=body["organisation_zip"],
            org_place=body["organisation_place"],
        )

    organisation.members.add(user)
    organisation.save()

    _attendance_list = []
    for key in body.keys():
        if key.startswith("attendance_"):
            att_id = key.split("_")[1]
            _attendance_list.append(
                {"id": att_id, "value": int(body.get(f"attendancecount_{att_id}"), 0)}
            )

    _asset_list = []
    for key in body.keys():
        if key.startswith("assetrequired_"):
            asset_id = key.split("_")[1]
            _asset_list.append(
                {"id": asset_id, "value": int(body.get(f"assetcount_{asset_id}", 1))}
            )

    try:
        exhibitor = Exhibitor.objects.get(organisation=organisation, event=event)
    except Exhibitor.DoesNotExist:
        exhibitor = Exhibitor.objects.create(
            event=event,
            organisation=organisation,
            general_note=body.get("general_note"),
        )

        for attendance in _attendance_list:
            attendance_exhibitor = ExhibitorAttendance.objects.create(
                exhibitor=exhibitor,
                day=Attendance.objects.get(id=attendance["id"]),
                count=attendance["value"],
            )

            attendance_exhibitor.save()

        for asset in _asset_list:
            asset_exhibitor = ExhibitorAsset.objects.create(
                exhibitor=exhibitor,
                asset=Asset.objects.get(id=asset["id"]),
                count=asset["value"],
            )

            asset_exhibitor.save()

    if created_user:
        return JsonResponse({"status": "created", "message": "User created"})
    elif not created_user:
        return JsonResponse({"status": "exists", "message": "User already exists"})
    else:
        return JsonResponse(
            {"status": "error", "message": "Something went horribly wrong"}, status=500
        )
