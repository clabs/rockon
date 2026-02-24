from __future__ import annotations

from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.status import StatusOut
from rockon.api.schemas.user_email import UpdateEmailIn
from rockon.base.models import EmailVerification

userEmailRouter = Router()


@userEmailRouter.post(
    '/',
    response=StatusOut,
    url_name='user_email_update',
    auth=django_auth,
)
def update_user_email(request, data: UpdateEmailIn):
    """Request an email address change for the authenticated user."""
    if data.changeEmailNew != data.changeEmailRepeat:
        return {'status': 'error', 'message': 'E-Mail is required'}

    EmailVerification.objects.filter(user=request.user).delete()
    EmailVerification.create_and_send(
        user=request.user, new_email=data.changeEmailNew.lower()
    )

    return {'status': 'ok', 'message': 'E-Mail updated'}
