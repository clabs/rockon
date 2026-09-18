from __future__ import annotations

from uuid import UUID

from ninja import Field, Schema


class CrewSignupIn(Schema):
    crew_shirt: UUID
    nutrition_type: str = ''
    nutrition_note: str = ''
    skills_note: str = ''
    attendance_note: str = ''
    stays_overnight: bool = False
    general_note: str = ''
    needs_leave_of_absence: bool = False
    leave_of_absence_note: str = ''
    skill_ids: list[UUID] = Field(default_factory=list)
    attendance_ids: list[UUID] = Field(default_factory=list)
    teamcategory_ids: list[UUID] = Field(default_factory=list)
    team_ids: list[UUID] = Field(default_factory=list)


class CrewSignupOut(Schema):
    status: str
    message: str = ''
    crew_member_state: str = ''
