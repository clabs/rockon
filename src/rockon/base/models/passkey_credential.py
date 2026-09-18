from __future__ import annotations

from django.contrib.auth.models import User

from rockon.library.custom_model import CustomModel, models


class PasskeyCredential(CustomModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='passkey_credentials'
    )
    # base64url-encoded credential ID — lookup key during authentication
    credential_id = models.TextField(unique=True)
    # CBOR-encoded COSE public key blob returned by py_webauthn
    public_key = models.BinaryField()
    # monotonically increasing counter; replay attack protection
    sign_count = models.PositiveBigIntegerField(default=0)
    aaguid = models.TextField(blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    device_info = models.CharField(max_length=255, blank=True, default='')
    last_used_at = models.DateTimeField(null=True, default=None, blank=True)

    def __str__(self):
        return f'{self.user} — {self.name or self.credential_id[:12]}'

    class Meta:
        ordering = ('user', 'created_at')
