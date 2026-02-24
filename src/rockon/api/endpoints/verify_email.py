from __future__ import annotations

from django.contrib.auth import login
from django.core import exceptions
from django.urls import reverse
from ninja import Router

from rockon.api.schemas.status import StatusOut
from rockon.api.schemas.verify_email import VerifyEmailIn, VerifyEmailOut
from rockon.base.models import EmailVerification

verifyEmailRouter = Router()


@verifyEmailRouter.post(
    '/',
    response={200: VerifyEmailOut, 201: VerifyEmailOut, 400: StatusOut},
    url_name='verify_email',
)
def verify_email(request, data: VerifyEmailIn):
    """Verify an email address using a token."""
    try:
        verification = EmailVerification.objects.select_related('user').get(
            token=data.token
        )
        if not verification.is_active:
            return 201, {'status': 'token_spent'}
        user = verification.user
        user.profile.email_is_verified = True
        if verification.new_email:
            user.email = verification.new_email
            user.username = verification.new_email
        user.save()
        verification.is_active = False
        verification.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return 200, {'status': 'verified', 'next': reverse('base:account')}
    except (
        EmailVerification.DoesNotExist,
        exceptions.ValidationError,
    ):
        return 400, {'status': 'error'}
