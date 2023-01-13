from __future__ import annotations

# WONTFIX: stop black and isort from messing up the imports
# fmt: off
from .magic_link import (magic_link, request_magic_link,
                         request_magic_link_submitted)
from .verify_email import verify_email

# fmt: on
