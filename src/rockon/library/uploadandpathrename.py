from __future__ import annotations

from pathlib import Path

from django.utils.deconstruct import deconstructible


@deconstructible
class UploadToPathAndRename:
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = Path(filename).suffix.lstrip('.')
        filename = f'{instance.id}.{ext}'
        return str(Path(self.sub_path) / filename)
