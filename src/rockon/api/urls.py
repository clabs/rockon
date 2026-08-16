from __future__ import annotations

from django.urls import path
from ninja import NinjaAPI

from .endpoints import (
    accountCreate,
    bandMediaRouter,
    bandmemberSignupRouter,
    bandRouter,
    bandVote,
    commentRouter,
    crewDateResponse,
    crewSignupRouter,
    exhibitorAdmin,
    exhibitorSignup,
    markVoucher,
    passkeyRouter,
    requestMagicLink,
    timeslotRouter,
    trackRouter,
    userEmailRouter,
    userProfileRouter,
    verifyEmailRouter,
)

api = NinjaAPI(urls_namespace='apiv2')

api.add_router('account-create', accountCreate)
api.add_router('bands/', bandRouter)
api.add_router('band-media/', bandMediaRouter)
api.add_router('band-votes/', bandVote)
api.add_router('bandmember-signup', bandmemberSignupRouter)
api.add_router('comments/', commentRouter)
api.add_router('crew-date-responses/', crewDateResponse)
api.add_router('crew-signup/', crewSignupRouter)
api.add_router('exhibitor-admin/', exhibitorAdmin)
api.add_router('exhibitor-signup/', exhibitorSignup)
api.add_router('timeslots/', timeslotRouter)
api.add_router('mark-voucher', markVoucher)
api.add_router('passkey/', passkeyRouter)
api.add_router('request-magic-link', requestMagicLink)
api.add_router('tracks/', trackRouter)
api.add_router('user-email', userEmailRouter)
api.add_router('user-profile', userProfileRouter)
api.add_router('verify-email', verifyEmailRouter)

urlpatterns = [
    path('v2/', api.urls),
]
