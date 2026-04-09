from ninja import Router
from django.contrib.auth.models import User
from django.shortcuts import aget_object_or_404

from rockon.api.schemas import RequestMagicLinkIn, RequestMagicLinkOut
from rockon.base.models import MagicLink

requestMagicLink = Router()


@requestMagicLink.post('', response=RequestMagicLinkOut, url_name='request_magic_link')
async def request_login(_request, data: RequestMagicLinkIn):
    email = data.email.strip().lower()
    user = await aget_object_or_404(User, email=email, is_active=True)
    await MagicLink.acreate_and_send(user)
    return {'status': 'ok', 'message': 'Magic link sent if mail matches a user.'}
