from __future__ import annotations

import json
from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.timezone import make_aware

from crew.models import Crew, CrewMember, Shirt
from crm.models import EmailVerification


def crew_signup(request, slug):
    created_user = False
    # FIXME: refactor to Django forms to validate input
    body = json.loads(request.body)

    _skills = [
        k.split("_")[1] for k, v in body.items() if k.startswith("skill_") and v == "on"
    ]
    _attendance = [
        k.split("_")[1]
        for k, v in body.items()
        if k.startswith("attendance_") and v == "on"
    ]
    _teams = [
        k.split("_")[1] for k, v in body.items() if k.startswith("team_") and v == "on"
    ]

    crew = Crew.objects.get(event__slug=slug)
    event = crew.event

    try:
        user = User.objects.get(email=body["user_email"])
        return HttpResponseBadRequest("User already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=body["user_email"],
            email=body["user_email"],
            password=None,
            first_name=body["user_first_name"],
            last_name=body["user_last_name"],
        )

        user.save()

        # FIXME: need try create and catch IntegrityError

        user.profile.nick_name = body.get("user_nick_name")
        user.profile.phone = body.get("user_mobile")
        user.profile.address = body.get("user_address")
        user.profile.address_housenumber = body.get("user_address_housenumber")
        user.profile.address_extension = body.get("user_address_extension")
        user.profile.zip_code = body.get("user_zipcode")
        user.profile.place = body.get("user_place")

        EmailVerification.create_and_send(user=user)

        created_user = True

    user.profile.events.add(event)
    user.save()

    try:
        crew_member = CrewMember.objects.get(
            user__last_name=body.get("user_last_name"),
            user__email=body.get("user_email"),
        )
    except CrewMember.DoesNotExist:
        _birthday = make_aware(datetime.strptime(body.get("user_birthday"), "%Y-%m-%d"))

        crew_member = CrewMember.objects.create(
            user=user,
            birthday=_birthday,
            crew=crew,
            shirt=Shirt.objects.get(id=body.get("crew_shirt")),
            nutrition=body.get("nutriton_type"),
            nutrition_note=body.get("nutrition_note"),
            skills_note=body.get("skills_note"),
            attendance_note=body.get("attendance_note"),
            stays_overnight=body.get("stays_overnight") == "on",
            general_note=body.get("general_note"),
            needs_leave_of_absence=body.get("leave_of_absence") == "on",
            leave_of_absence_note=body.get("leave_of_absence_note"),
        )

    for skill in _skills:
        crew_member.skills.add(skill)
    for attendance in _attendance:
        crew_member.attendance.add(attendance)
    for team in _teams:
        crew_member.teams.add(team)
    crew_member.save()

    if created_user:
        return JsonResponse({"status": "created", "message": "User created"})
    elif not created_user:
        return JsonResponse({"status": "exists", "message": "'User already exists"})
    else:
        return JsonResponse(
            {"status": "error", "message": "Something went horribly wrong"}, status=500
        )
