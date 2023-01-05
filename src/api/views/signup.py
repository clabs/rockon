from __future__ import annotations

import json
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.http import JsonResponse
from django.template import loader
from django.utils.timezone import make_aware

from crew.models import Crew, CrewMember, Shirt
from crm.models import EmailVerification, MagicLink, Person


def signup(request, slug):
    created_person = False
    # FIXME: refactor to Django forms to validate input and use Django's CSRF protection
    body = json.loads(request.body)

    # FIXME: refactor this with Django forms
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
        person = Person.objects.get(
            email=body.get("person_email"), last_name=body.get("person_lastname")
        )
    except Person.DoesNotExist:
        # FIXME: need try create and catch IntegrityError
        person = Person.objects.create(
            first_name=body.get("person_firstname"),
            last_name=body.get("person_lastname"),
            nickname=body.get("person_nickname"),
            email=body.get("person_email"),
            phone=body.get("person_mobile"),
            address=body.get("person_address"),
            address_housenumber=body.get("person_housenumber"),
            address_extension=body.get("person_address_extension"),
            zip_code=body.get("person_zipcode"),
            place=body.get("person_place"),
        )

        email_verifcation = EmailVerification.objects.create(person=person)
        email_verifcation.save()

        # FIXME: this should use a worker queue in redis or something
        # FIXME: import the scheme, domain and rest of things from Django settings
        # FIXME: use absolute URLs in templates
        # FIXME: create a helper class for mailings with defined textfields to replace.
        template = loader.get_template("mail/confirm_email_address.html")

        context = {
            "name": person.first_name,
            "email_verification_token": email_verifcation.token,
        }

        send_mail(
            "Bitte bestätige deine E-Mail-Adresse",
            f"Hallo {person.first_name},\nbitte bestätige deine E-Mail-Adresse in dem du diesen Link aufrufst:\nhttp://localhost:8000/crm/verify-email/{email_verifcation.token}",
            "rockon@example.com",
            [f"{person.email}"],
            html_message=template.render(context),
            fail_silently=False,
        )

        created_person = True

    person.events.add(event)
    person.save()

    try:
        crew_member = CrewMember.objects.get(
            person__last_name=body.get("person_lastname"),
            person__email=body.get("person_email"),
        )
    except CrewMember.DoesNotExist:
        _birthday = make_aware(
            datetime.strptime(body.get("person_birthday"), "%Y-%m-%d")
        )

        crew_member = CrewMember.objects.create(
            person=person,
            birthday=_birthday,
            crew=crew,
            shirt=Shirt.objects.get(id=body.get("crew_shirt")),
            nutrition=body.get("nutriton_type"),
            nutrition_note=body.get("nutrition_note"),
            skills_note=body.get("skills_note"),
            attendance_note=body.get("attendance_note"),
            overnight=body.get("overnight") == "on",
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

    if created_person:
        return JsonResponse({"status": "created", "message": "Person created"})
    elif not created_person:
        return JsonResponse({"status": "exists", "message": "Person already exists"})
    else:
        return JsonResponse(
            {"status": "error", "message": "Something went horribly wrong"}, status=500
        )


def request_magic_link(request):
    try:
        body = json.loads(request.body)
        person = Person.objects.get(
            email=body.get("contact_email"), last_name=body.get("person_lastname")
        )

        old_links = MagicLink.objects.filter(person=person)
        if old_links:
            old_links.delete()

        _expires_at = make_aware(datetime.now() + timedelta(weeks=4))

        # FIXME: this should be a setting
        # FIXME: improve timedelta handling
        magic_link = MagicLink.objects.create(person=person, expires_at=_expires_at)
        magic_link.save()

        # FIXME: this should use a worker queue in redis or something
        # FIXME: import the scheme, domain and rest of things from Django settings
        # FIXME: use absolute URLs in templates
        # FIXME: create a helper class for mailings with defined textfields to replace.
        template = loader.get_template("mail/magic_link.html")
        context = {
            "name": person.first_name,
            "magic_link_token": magic_link.token,
            "expires_at": _expires_at,
        }
        send_mail(
            "Dein rockon Magic Link",
            f"Hallo {person.first_name},\nhier findest du deinen persönlichen Link zum einsehen und ändern deiner persönlichen Daten:\nhttp://localhost:8000/crm/magic-link/{magic_link.token}",
            "rockon@example.com",
            [f"{person.email}"],
            html_message=template.render(context),
            fail_silently=False,
        )
    except person.DoesNotExist:
        pass

    # FIXME: this should be a page
    return JsonResponse(
        {"status": "ok", "message": "Magic link sent if mail and lastname match"}
    )
