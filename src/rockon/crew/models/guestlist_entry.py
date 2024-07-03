from __future__ import annotations

from rockon.crew.models import crew_member
from rockon.library.custom_model import CustomModel, models

from .attendance import Attendance
from .crew_member import CrewMember


class GuestListEntry(CustomModel):
    """Guestlist entry model."""

    crew_member = models.ForeignKey(
        CrewMember, on_delete=models.CASCADE, related_name="guestlist_entries"
    )
    voucher = models.CharField(max_length=96, unique=True)
    day = models.ForeignKey(
        Attendance, on_delete=models.CASCADE, related_name="guestlist_entries"
    )
    send = models.BooleanField(default=False)
