from __future__ import annotations

from os import path

from django.utils.deconstruct import deconstructible


@deconstructible
class UploadToPathAndRename:
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]
        filename = f"{instance.id}.{ext}"
        return path.join(self.sub_path, filename)
