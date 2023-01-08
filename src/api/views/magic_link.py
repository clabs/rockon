from __future__ import annotations

import json
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.http import JsonResponse
from django.template import loader
from django.utils.timezone import make_aware
from django_q.tasks import async_task

from crm.models import MagicLink, Person


def request_magic_link(request):
    try:
        body = json.loads(request.body)
        person = Person.objects.get(
            email=body.get("contact_email"), last_name=body.get("person_lastname")
        )

        MagicLink.objects.filter(person=person).delete()

        _expires_at = make_aware(datetime.now() + timedelta(weeks=4))

        # FIXME: this should be a setting
        # FIXME: improve timedelta handling
        magic_link = MagicLink.objects.create(person=person, expires_at=_expires_at)
        magic_link.save()

        # FIXME: import the scheme, domain and rest of things from Django settings
        # FIXME: use absolute URLs in templates
        # FIXME: create a helper class for mailings with defined textfields to replace.
        template = loader.get_template("mail/magic_link.html")
        context = {
            "name": person.first_name,
            "magic_link_token": magic_link.token,
            "expires_at": _expires_at,
        }

        async_task(
            send_mail,
            subject="Dein rockon Magic Link",
            message=f"Hallo {person.first_name},\nhier findest du deinen persönlichen Link zum einsehen und ändern deiner persönlichen Daten:\nhttp://localhost:8000/crm/magic-link/{magic_link.token}",
            from_email="rockon@example.com",
            recipient_list=[f"{person.email}"],
            html_message=template.render(context),
            fail_silently=False,
        )

    except person.DoesNotExist:
        pass

    return JsonResponse(
        {"status": "ok", "message": "Magic link sent if mail and lastname match"}
    )
