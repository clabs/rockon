from __future__ import annotations

import re
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.forms import model_to_dict
from django.template import loader
from django_q.tasks import async_task

from .custom_model import CustomModel
from .event import Event
from .region import Region
from .track import Track


class Bid(CustomModel):
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    style = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey(
        "Region", on_delete=models.SET_NULL, related_name="bids", blank=True, null=True
    )
    bandname = models.CharField(max_length=255, blank=True, null=True)
    student = models.BooleanField(default=False)
    managed = models.BooleanField(default=False)
    style = models.CharField(max_length=255, blank=True, null=True)
    letter = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    mail = models.EmailField(null=True, blank=True)
    url = models.URLField(max_length=255, blank=True, null=True)
    fb = models.URLField(max_length=255, blank=True, null=True)
    track = models.ForeignKey(
        Track, on_delete=models.SET_NULL, related_name="bids", blank=True, null=True
    )

    def __str__(self):
        if self.bandname:
            return self.bandname
        return f"Bid {self.id}"

    class Meta:
        ordering = ["created"]

    def send_welcome_mail(self):
        bid_link = f"http://localhost:4711/#/bewerbung/{self.id}"
        template = loader.get_template("mail/bblegacy_bid_registered.html")
        extra_context = {
            "recipient": f"{self.mail}",
            "subject": f"{self.event.name} - Deine Anmeldung",
            "bid_link": bid_link,
            "closing_date": self.event.closing_date.strftime("%d.%m.%Y"),
        }

        message = f'Vielen Dank für Deine Anmeldung!\nBis zum { extra_context["closing_date"] } \
        habt Ihr Zeit Eure Bewerbung zu bearbeiten.\n \
        { extra_context["bid_link"] }\n\
        Anfang März 2024 machen wir die Auswahl und melden uns kurz darauf bei Euch.\n\
        Gruß Euer ROCKTREFF-Team'

        async_task(
            send_mail,
            subject=extra_context["subject"],
            message=message,
            from_email=settings.EMAIL_DEFAULT_FROM,
            recipient_list=[extra_context["recipient"]],
            html_message=template.render(extra_context),
            fail_silently=False,
        )

    def update_from_json(self, json: dict[str, Any]) -> Bid:
        try:
            region = Region.objects.get(id=json.get("region"))
        except Region.DoesNotExist:
            region = self.region or None
        try:
            self.style = json.get("style", self.style)
            self.region = region
            self.bandname = json.get("bandname", self.bandname)
            self.student = json.get("student", self.student)
            self.style = json.get("style", self.style)
            self.letter = json.get("letter", self.letter)
            self.url = json.get("url", self.url)
            self.fb = json.get("fb", self.fb)
            self.save()
        except ValidationError:
            raise Exception("Invalid data")

        return self

    def to_json(self) -> dict[str, Any]:
        _self = model_to_dict(self)

        _self["media"] = [media.id for media in self.media.all()]
        _self["votes"] = [vote.id for vote in self.votes.all()]
        _self["notes"] = []

        return _self

    @classmethod
    def create_from_json(cls, json) -> Bid:
        try:
            event = Event.objects.get(id=json["event"])
        except Event.DoesNotExist:
            raise Exception("Event does not exist")

        try:
            new_bid = cls.objects.create(
                event=event,
                student=json.get("student"),
                managed=json.get("managed"),
                contact=json.get("contact"),
                phone=json.get("phone"),
                mail=json.get("mail"),
            )
        except ValidationError:
            raise Exception("Invalid data")

        return new_bid
