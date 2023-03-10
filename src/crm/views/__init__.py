from __future__ import annotations

from .logout import logout_page

# WONTFIX: stop black and isort from messing up the imports
# fmt: off
from .magic_link import magic_link, request_magic_link
from .user_home import get_user_homeview
from .user_profile import get_user_profile
from .verify_email import verify_email

# fmt: on
