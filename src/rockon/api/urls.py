from __future__ import annotations

from django.urls import include, path
from ninja import NinjaAPI

from rockon.api.views import (
    band_techrider,
    bandmember_signup,
    crew_signup,
    update_user_email,
    update_user_profile,
    verify_email,
)

from .endpoints import (
    accountCreate,
    bandMediaRouter,
    bandRouter,
    bandVote,
    commentRouter,
    exhibitorSignup,
    markVoucher,
    requestMagicLink,
    trackRouter,
)

api = NinjaAPI(urls_namespace='apiv2')

api.add_router('account-create', accountCreate)
api.add_router('bands/', bandRouter)
api.add_router('band-media/', bandMediaRouter)
api.add_router('band-votes/', bandVote)
api.add_router('comments/', commentRouter)
api.add_router('tracks/', trackRouter)
api.add_router('request-magic-link', requestMagicLink)
api.add_router('mark-voucher', markVoucher)
api.add_router('exhibitor-signup/', exhibitorSignup)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path('crm/crew/<slug:slug>/signup/', crew_signup, name='api_crew_signup'),
    path('crm/verify-email/', verify_email, name='api_crm_verify_email'),
    path('crm/update-email/', update_user_email, name='api_crm_update_email'),
    path('bands/bandmember/', bandmember_signup, name='api_bandmember_signup'),
    path(
        'crm/update-user-profile/',
        update_user_profile,
        name='api_crm_update_user_profile',
    ),
    path('bands/<slug:slug>/techrider/', band_techrider, name='api_band_techrider'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('v2/', api.urls),
]
