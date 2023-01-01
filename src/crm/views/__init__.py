from __future__ import annotations

# FIXME: stop black and isort from messing up the imports
# fmt: off
from .link_shortener import link_shortener
from .magic_link import (magic_link, request_magic_link,
                         request_magic_link_submitted)
from .verify_email import verify_email

# fmt: on
