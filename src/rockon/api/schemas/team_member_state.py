from __future__ import annotations

from ninja import Schema


class TeamMemberStateIn(Schema):
    event_team_id: str
    crewmember_id: str
    state: str


class TeamMemberStateOut(Schema):
    event_team_id: str
    crewmember_id: str
    state: str
