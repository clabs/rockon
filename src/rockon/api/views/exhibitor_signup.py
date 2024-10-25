from __future__ import annotations

import json

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template import loader
from django_q.tasks import async_task

from rockon.base.models import Event, Organisation
from rockon.exhibitors.models import (
    Asset,
    Attendance,
    Exhibitor,
    ExhibitorAsset,
    ExhibitorAttendance,
)


@user_passes_test(lambda u: u.groups.filter(name="exhibitors").exists())
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

    request.user.profile.events.add(event)
    request.user.save()

    try:
        organisation = Organisation.objects.get(id=body.get("org_id"))
    except Organisation.DoesNotExist:
        organisation = Organisation.objects.create(
            org_name=body["organisation_name"],
            org_address=body["organisation_address"],
            org_house_number=body["organisation_address_housenumber"],
            org_address_extension=body["organisation_address_extension"],
            org_zip=body["organisation_zip"],
            org_place=body["organisation_place"],
        )

    organisation.members.add(request.user)
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
            about_note=body.get("about_note"),
            offer_note=body.get("offer_note"),
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

        template = loader.get_template("mail/exhibitor_signup.html")
        extra_context = {
            "event_name": event.name,
            "organisation": organisation.org_name,
        }

        message = f"Hallo Admin-Team,\nes gibt eine neue Anmeldung eines Aussteller bei \
                    {{event.name}}. Bitte überprüft die Angaben und schaut ob alles stimmt."

        async_task(
            send_mail,
            subject=f"{settings.EMAIL_SUBJECT_PREFIX} Neue Ausstelleranmeldung",
            message=message,
            from_email=settings.EMAIL_DEFAULT_FROM,
            recipient_list=[
                user.email
                for user in Group.objects.get(name="exhibitor_admins").user_set.all()
            ],
            html_message=template.render(extra_context),
            fail_silently=False,
        )

    if created_user:
        return JsonResponse({"status": "created", "message": "User created"})
    elif not created_user:
        return JsonResponse({"status": "exists", "message": "User already exists"})
    else:
        return JsonResponse(
            {"status": "error", "message": "Something went horribly wrong"}, status=500
        )
