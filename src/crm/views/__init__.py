from __future__ import annotations

from .logout import logout_page

# WONTFIX: stop black and isort from messing up the imports
# fmt: off
from .magic_link import magic_link, request_magic_link, request_magic_link_submitted
from .user_profile import get_user_profile
from .verify_email import verify_email
from .misc import impressum, privacy
# fmt: on
