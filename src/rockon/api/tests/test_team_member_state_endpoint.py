from __future__ import annotations

import json
from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import (
    Crew,
    CrewMember,
    EventTeam,
    Team,
    TeamCategory,
    TeamMember,
)


def _make_event(slug: str = 'rocktreff-2026') -> Event:
    start = date(2026, 7, 1)
    return Event.objects.create(
        name='Rocktreff 2026',
        slug=slug,
        description='desc',
        start=start,
        end=start + timedelta(days=2),
        setup_start=start - timedelta(days=2),
        setup_end=start - timedelta(days=1),
        opening=start,
        closing=start + timedelta(days=1),
        teardown_start=start + timedelta(days=2),
        teardown_end=start + timedelta(days=3),
        location='Berlin',
        signup_type=SignUpType.CREW,
        signup_is_open=True,
    )


class TeamMemberStateEndpointTests(TestCase):
    def setUp(self):
        self.crewcoord_group = Group.objects.create(name='crewcoord')

        self.crewcoord_user = User.objects.create_user(
            username='coord',
            email='coord@example.com',
            password='secret',
            first_name='Coord',
            last_name='User',
        )
        self.crewcoord_user.groups.add(self.crewcoord_group)

        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='secret',
        )

        self.member_user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='secret',
            first_name='Alice',
            last_name='Member',
        )

        self.event_one = _make_event('rocktreff-2026')
        self.event_two = _make_event('rocktreff-2027')

        self.crew_one = Crew.objects.create(
            event=self.event_one, name='Crew 2026', year=2026
        )
        self.crew_two = Crew.objects.create(
            event=self.event_two, name='Crew 2027', year=2027
        )

        category = TeamCategory.objects.create(
            name='Technik', description='Technikteams'
        )
        self.team = Team.objects.create(
            name='Stage', description='Stage hands', category=category, is_public=True
        )
        self.team_other_event = Team.objects.create(
            name='Lights', description='Lights crew', category=category, is_public=True
        )

        self.event_team = EventTeam.objects.create(event=self.event_one, team=self.team)
        self.event_two_team = EventTeam.objects.create(
            event=self.event_two, team=self.team_other_event
        )

        self.crew_member = CrewMember.objects.create(
            user=self.member_user, crew=self.crew_one
        )
        self.crew_member_other_event = CrewMember.objects.create(
            user=self.member_user, crew=self.crew_two
        )

    def _url(self, slug: str) -> str:
        return f'/api/v2/team-members/{slug}/'

    def _patch(self, slug: str, payload: dict):
        payload = {
            key: (str(value) if key.endswith('_id') else value)
            for key, value in payload.items()
        }
        return self.client.patch(
            self._url(slug), data=json.dumps(payload), content_type='application/json'
        )

    def test_requires_authentication(self):
        response = self._patch(
            self.event_one.slug,
            {
                'event_team_id': self.event_team.id,
                'crewmember_id': self.crew_member.id,
                'state': 'confirmed',
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_requires_crewcoord_group(self):
        self.client.force_login(self.regular_user)

        response = self._patch(
            self.event_one.slug,
            {
                'event_team_id': self.event_team.id,
                'crewmember_id': self.crew_member.id,
                'state': 'confirmed',
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_updates_existing_team_member_state(self):
        team_member = TeamMember.objects.create(
            event_team=self.event_team, crewmember=self.crew_member, state='unknown'
        )
        self.client.force_login(self.crewcoord_user)

        response = self._patch(
            self.event_one.slug,
            {
                'event_team_id': self.event_team.id,
                'crewmember_id': self.crew_member.id,
                'state': 'confirmed',
            },
        )

        self.assertEqual(response.status_code, 200)
        team_member.refresh_from_db()
        self.assertEqual(team_member.state, 'confirmed')

    def test_creates_team_member_when_none_exists(self):
        self.client.force_login(self.crewcoord_user)
        self.assertFalse(
            TeamMember.objects.filter(
                event_team=self.event_team, crewmember=self.crew_member
            ).exists()
        )

        response = self._patch(
            self.event_one.slug,
            {
                'event_team_id': self.event_team.id,
                'crewmember_id': self.crew_member.id,
                'state': 'confirmed',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            TeamMember.objects.get(
                event_team=self.event_team, crewmember=self.crew_member
            ).state,
            'confirmed',
        )

    def test_rejects_invalid_state(self):
        self.client.force_login(self.crewcoord_user)

        response = self._patch(
            self.event_one.slug,
            {
                'event_team_id': self.event_team.id,
                'crewmember_id': self.crew_member.id,
                'state': 'bogus',
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            TeamMember.objects.filter(
                event_team=self.event_team, crewmember=self.crew_member
            ).exists()
        )

    def test_rejects_event_team_from_other_event(self):
        self.client.force_login(self.crewcoord_user)

        response = self._patch(
            self.event_one.slug,
            {
                'event_team_id': self.event_two_team.id,
                'crewmember_id': self.crew_member.id,
                'state': 'confirmed',
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            TeamMember.objects.filter(
                event_team=self.event_two_team, crewmember=self.crew_member
            ).exists()
        )

    def test_rejects_crewmember_from_other_event(self):
        self.client.force_login(self.crewcoord_user)

        response = self._patch(
            self.event_one.slug,
            {
                'event_team_id': self.event_team.id,
                'crewmember_id': self.crew_member_other_event.id,
                'state': 'confirmed',
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            TeamMember.objects.filter(
                event_team=self.event_team, crewmember=self.crew_member_other_event
            ).exists()
        )

    def test_unknown_event_slug(self):
        self.client.force_login(self.crewcoord_user)

        response = self._patch(
            'unknown-event',
            {
                'event_team_id': self.event_team.id,
                'crewmember_id': self.crew_member.id,
                'state': 'confirmed',
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_clears_invalid_team_roles_on_state_change(self):
        team_member = TeamMember.objects.create(
            event_team=self.event_team, crewmember=self.crew_member, state='confirmed'
        )
        self.event_team.lead = self.member_user
        self.event_team.save(update_fields=['lead'])
        self.client.force_login(self.crewcoord_user)

        response = self._patch(
            self.event_one.slug,
            {
                'event_team_id': self.event_team.id,
                'crewmember_id': self.crew_member.id,
                'state': 'rejected',
            },
        )

        self.assertEqual(response.status_code, 200)
        team_member.refresh_from_db()
        self.assertEqual(team_member.state, 'rejected')
        self.event_team.refresh_from_db()
        self.assertIsNone(self.event_team.lead_id)
