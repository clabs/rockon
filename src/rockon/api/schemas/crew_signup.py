from __future__ import annotations

from ninja import Schema


class CrewSignupIn(Schema):
    crew_shirt: int
    nutrition_type: str = ''
    nutrition_note: str = ''
    skills_note: str = ''
    attendance_note: str = ''
    stays_overnight: bool = False
    general_note: str = ''
    needs_leave_of_absence: bool = False
    leave_of_absence_note: str = ''
    skill_ids: list[int] = []
    attendance_ids: list[int] = []
    teamcategory_ids: list[int] = []
    team_ids: list[int] = []
