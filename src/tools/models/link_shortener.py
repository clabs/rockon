from __future__ import annotations

from secrets import randbits

from library.custom_model import CustomModel, models

BASE_ALPH = tuple("023456789ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghikmnopqrstuvwxyz")
BASE_DICT = {c: v for v, c in enumerate(BASE_ALPH)}
BASE_LEN = len(BASE_ALPH)


# inspired by from https://stackoverflow.com/a/14259141/16174836


class LinkShortener(CustomModel):
    """LinkShortener model."""

    url = models.URLField()
    slug = models.SlugField(unique=True)
    comment = models.TextField()
    counter = models.IntegerField(default=0)

    def __str__(self: LinkShortener):
        return str(self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.base_encode(randbits(32))
        super().save(*args, **kwargs)

    def base_encode(self, num):
        if not num:
            return None

        encoding = ""
        while num:
            num, rem = divmod(num, BASE_LEN)
            encoding = BASE_ALPH[rem] + encoding
        return encoding

    def base_decode(self, string):
        num = 0
        for char in string:
            num = num * BASE_LEN + BASE_DICT[char]
        return num
