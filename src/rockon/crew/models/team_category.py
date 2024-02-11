from __future__ import annotations

from django.templatetags.static import static

from rockon.library import UploadToPathAndRename
from rockon.library.custom_model import CustomModel, models


class TeamCategory(CustomModel):
    name = models.CharField(max_length=1024)
    description = models.TextField()
    image = models.ImageField(
        upload_to=UploadToPathAndRename("teams"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Team categories"

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static("assets/4_3_placeholder.webp")
