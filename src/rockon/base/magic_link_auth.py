from __future__ import annotations

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from rockon.base.models import MagicLink


class MagicLinkAuth(BaseBackend):
    def authenticate(self, request, token=None):
        # Check the token and return a user.
        try:
            magic_link = MagicLink.objects.select_related('user').get(token=token)
            return magic_link.user
        except MagicLink.DoesNotExist, User.DoesNotExist:
            return None
