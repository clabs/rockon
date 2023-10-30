from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from bblegacy.helper import (
    blob_to_file,
    create_image_thumbnail,
    delete_media_file,
    encode_mp3_file,
    get_image_metadata,
)

from .bid import Bid
from .custom_model import CustomModel


class Media(CustomModel):
    bid = models.ForeignKey("Bid", on_delete=models.CASCADE, related_name="media")
    type = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    meta = models.CharField(max_length=512, default=0)
    mimetype = models.CharField(max_length=255, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    filesize = models.FloatField(blank=True, null=True)

    def __str__(self):
        if self.filename:
            return self.filename
        return self.id

    class Meta:
        ordering = ["bid", "type"]
        verbose_name = "Media"
        verbose_name_plural = "Medien"

    def update_from_json(self, json) -> Media:
        try:
            self.type = json.get("type")
            self.mimetype = json.get("mimetype")
            self.filename = json.get("filename")
            self.filesize = json.get("filesize")
            self.save()
        except ValidationError:
            raise Exception

        blob = json.get("blob")

        if blob:
            filename = blob_to_file(self, blob)
            self.filename = filename
            self.url = (
                f"{settings.DOMAIN}{settings.MEDIA_URL}bids/{self.bid.id}/{self.id}"
            )
            self.meta = get_image_metadata(self)
            self.save()
            if self.type in ["picture", "logo"]:
                print("create thumbnail")
                create_image_thumbnail(self)

    @classmethod
    def create_from_json(cls, json) -> Media:
        try:
            bid = Bid.objects.get(id=json["bid"])
        except Bid.DoesNotExist:
            raise Exception

        try:
            new_media = cls.objects.create(
                bid=bid,
                type=json.get("type"),
                url=json.get("url"),
                mimetype=json.get("mimetype"),
                filename=json.get("filename"),
                filesize=json.get("filesize"),
            )
        except ValidationError:
            raise Exception

        blob = json.get("blob")

        if blob:
            filename = blob_to_file(new_media, blob)
            new_media.filename = filename
            new_media.url = f"{settings.DOMAIN}{settings.MEDIA_URL}bids/{new_media.bid.id}/{new_media.id}"
            new_media.meta = get_image_metadata(new_media)
            new_media.save()

            if new_media.type in ["picture", "logo"]:
                create_image_thumbnail(new_media)
            if new_media.type == "audio":
                encode_mp3_file(new_media)

        return new_media

    @classmethod
    def remove(cls, id: str) -> None:
        try:
            media = cls.objects.get(id=id)
        except cls.DoesNotExist:
            return None
        if media.filename:
            delete_media_file(media)
        media.delete()
