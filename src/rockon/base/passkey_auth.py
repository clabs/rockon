from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from rockon.base.models import PasskeyCredential


class PasskeyAuth(BaseBackend):
    def authenticate(self, request, credential_id=None):
        if credential_id is None:
            return None
        try:
            credential = PasskeyCredential.objects.select_related('user').get(
                credential_id=credential_id
            )
            return credential.user
        except PasskeyCredential.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
