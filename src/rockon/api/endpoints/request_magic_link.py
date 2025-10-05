from ninja import Router
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rockon.api.schemas import RequestMagicLinkIn, RequestMagicLinkOut
from rockon.base.models import MagicLink

requestMagicLink = Router()


@requestMagicLink.post('', response=RequestMagicLinkOut, url_name='request_magic_link')
def request_login(request, data: RequestMagicLinkIn):
    user = get_object_or_404(User, email=data.email)
    MagicLink.create_and_send(user)
    return {'status': 'ok', 'message': 'Magic link sent if mail matches a user.'}
