# Routes

## Base

/ -> Homepage with current events
/home/ -> Homepage, planned with news

## Account

/account/ -> Profile page
/account/login/ -> Request magic link
/account/login/<token> -> Login with magic link
/account/logout/ -> Logout
/account/register/?ctx= -> Register
/account/verify/<token> -> Verify email

## Crew

/crew/ -> Forward to /crew/join/
/crew/join/ -> forward to /crew/join/<slug>/
/crew/join/<slug>/ -> Preselect Login or Register
/crew/join/<slug>/ -> Join crew with slug

## Bands

/bands/
/bands/bid/ -> forward to /bands/bid/<slug>/ current event
/bands/bid/<slug>/ -> Apply as band for event with slug
/bands/bid/<slug>/new/ -> Create new band bid and forward
/bands/bid/<slug>/<guid>/ -> View band bid
