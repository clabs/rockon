from ninja import Router
from django.contrib.auth.models import User

from rockon.api.schemas import RequestMagicLinkIn, RequestMagicLinkOut
from rockon.base.models import MagicLink

requestMagicLink = Router()


@requestMagicLink.post('', response=RequestMagicLinkOut, url_name='request_magic_link')
async def request_login(request, data: RequestMagicLinkIn):
    email = data.email.strip().lower()
    try:
        user = await User.objects.aget(email=email, is_active=True)
        await MagicLink.acreate_and_send(user)
    except User.DoesNotExist:
        pass
    return {'status': 'ok', 'message': 'Magic link sent if mail matches a user.'}
