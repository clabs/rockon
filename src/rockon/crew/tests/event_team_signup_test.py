from __future__ import annotations

import json
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event, UserProfile
from rockon.base.models.event import SignUpType
from rockon.crew.models import Crew, EventTeam, Shirt, Team, TeamCategory, TeamMember
from rockon.crew.models.shirt import ShirtCut, ShirtSize


class EventScopedTeamSignupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='crew-user',
            email='crew@example.com',
            password='secret',
            first_name='Crew',
            last_name='User',
        )
        profile = UserProfile.objects.get(user=self.user)
        profile.phone = '030123456'
        profile.address = 'Teststrasse'
        profile.address_housenumber = '42'
        profile.zip_code = '10999'
        profile.place = 'Berlin'
        profile.birthday = date(1990, 1, 1)
        profile.save()

        self.event_one = self._create_event('Rocktreff 2026', 'rocktreff-2026', 0)
        self.event_two = self._create_event('Rocktreff 2027', 'rocktreff-2027', 30)
        self.crew_one = Crew.objects.create(
            event=self.event_one, name='Crew 2026', year=2026
        )
        self.crew_two = Crew.objects.create(
            event=self.event_two, name='Crew 2027', year=2027
        )
        self.shirt = Shirt.objects.create(size=ShirtSize.M, cut=ShirtCut.STRAIGHT)

        self.shared_category = TeamCategory.objects.create(
            name='Technik',
            description='Technikteams',
        )
        self.hidden_category = TeamCategory.objects.create(
            name='Awareness',
            description='Nur fuer das andere Event',
        )

        self.stage_team = Team.objects.create(
            name='Stage',
            description='Stage hands',
            category=self.shared_category,
            is_public=True,
        )
        self.light_team = Team.objects.create(
            name='Lights',
            description='Lights crew',
            category=self.shared_category,
            is_public=True,
        )
        self.awareness_team = Team.objects.create(
            name='Awareness Team',
            description='Awareness crew',
            category=self.hidden_category,
            is_public=True,
        )

        self.stage_event_team = EventTeam.objects.create(
            event=self.event_one,
            team=self.stage_team,
        )
        self.light_event_team = EventTeam.objects.create(
            event=self.event_two,
            team=self.light_team,
        )
        self.awareness_event_team = EventTeam.objects.create(
            event=self.event_two,
            team=self.awareness_team,
        )

    def _create_event(self, name: str, slug: str, offset_days: int) -> Event:
        start = date(2026, 7, 1) + timedelta(days=offset_days)
        return Event.objects.create(
            name=name,
            slug=slug,
            description=f'{name} description',
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

    def _signup_payload(
        self, *, team_ids: list[str], teamcategory_ids: list[str]
    ) -> dict:
        return {
            'crew_shirt': str(self.shirt.id),
            'nutrition_type': '',
            'nutrition_note': '',
            'skills_note': '',
            'attendance_note': '',
            'stays_overnight': False,
            'general_note': '',
            'needs_leave_of_absence': False,
            'leave_of_absence_note': '',
            'skill_ids': [],
            'attendance_ids': [],
            'teamcategory_ids': teamcategory_ids,
            'team_ids': team_ids,
        }

    @patch(
        'rockon.base.models.user_profile.UserProfile.is_profile_complete_crew',
        return_value=True,
    )
    def test_join_view_only_shows_teams_for_requested_event(self, _is_complete):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('crew:join', kwargs={'slug': self.event_one.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.shared_category.name)
        self.assertContains(response, self.stage_team.name)
        self.assertNotContains(response, self.light_team.name)
        self.assertNotContains(response, self.hidden_category.name)
        self.assertNotContains(response, self.awareness_team.name)

    def test_signup_creates_membership_for_event_team_only(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event_one.slug}/',
            data=json.dumps(
                self._signup_payload(
                    team_ids=[str(self.stage_event_team.id)],
                    teamcategory_ids=[str(self.shared_category.id)],
                )
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        crew_member = TeamMember.objects.get(
            crewmember__user=self.user,
            crewmember__crew=self.crew_one,
        ).crewmember
        membership = TeamMember.objects.get(crewmember=crew_member)
        self.assertEqual(membership.event_team, self.stage_event_team)
        self.assertEqual(list(crew_member.interested_in.all()), [self.shared_category])

    def test_signup_rejects_team_from_other_event(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event_one.slug}/',
            data=json.dumps(
                self._signup_payload(
                    team_ids=[str(self.light_event_team.id)],
                    teamcategory_ids=[str(self.shared_category.id)],
                )
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                'status': 'error',
                'message': 'Invalid team selection for event',
            },
        )
        self.assertFalse(
            TeamMember.objects.filter(
                crewmember__user=self.user,
                crewmember__crew=self.crew_one,
            ).exists()
        )
