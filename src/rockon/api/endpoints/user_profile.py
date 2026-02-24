from __future__ import annotations

from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.status import StatusOut
from rockon.api.schemas.user_profile import UserProfileIn

userProfileRouter = Router()


@userProfileRouter.post(
    '/',
    response=StatusOut,
    url_name='user_profile_update',
    auth=django_auth,
)
def update_user_profile(request, data: UserProfileIn):
    """Update the authenticated user's profile."""
    user = request.user

    user.first_name = data.first_name
    user.last_name = data.last_name
    user.save()

    profile = user.profile

    profile.nick_name = data.nick_name
    profile.phone = data.phone
    profile.address = data.address
    profile.address_extension = data.address_extension
    profile.address_housenumber = data.address_housenumber
    profile.zip_code = data.zip_code
    profile.place = data.place
    profile.birthday = data.user_birthday if data.user_birthday else None

    profile.save()

    return {'status': 'ok', 'message': 'Profile updated'}
