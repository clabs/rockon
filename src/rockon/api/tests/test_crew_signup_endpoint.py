from __future__ import annotations

import json
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import (
    Crew,
    CrewMember,
    EventTeam,
    Shirt,
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


def _base_payload(shirt_id, **kwargs) -> dict:
    return {
        'crew_shirt': str(shirt_id),
        'nutrition_type': 'omnivore',
        'nutrition_note': '',
        'skills_note': '',
        'attendance_note': '',
        'stays_overnight': False,
        'general_note': '',
        'needs_leave_of_absence': False,
        'leave_of_absence_note': '',
        'skill_ids': [],
        'attendance_ids': [],
        'teamcategory_ids': [],
        'team_ids': [],
        **kwargs,
    }


class CrewSignupEndpointTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='crewsignup-user',
            email='crew@example.com',
            password='secret',
            first_name='Crew',
            last_name='Person',
        )
        self.event = _make_event()
        self.crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)
        self.shirt = Shirt.objects.create(size='M', cut='straight')

        self.category = TeamCategory.objects.create(
            name='Technik', description='Technical teams'
        )
        self.team = Team.objects.create(
            name='Sound', description='Sound team', category=self.category
        )
        self.event_team = EventTeam.objects.create(event=self.event, team=self.team)

    def test_crew_signup_creates_new_crew_member(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(_base_payload(self.shirt.id)),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'status': 'ok', 'message': 'signed up for crew successfully'},
        )
        self.assertTrue(
            CrewMember.objects.filter(user=self.user, crew=self.crew).exists()
        )

    def test_crew_signup_updates_existing_crew_member(self):
        self.client.force_login(self.user)
        CrewMember.objects.create(user=self.user, crew=self.crew, shirt=self.shirt)

        new_shirt = Shirt.objects.create(size='L', cut='fitted')
        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(
                _base_payload(
                    new_shirt.id, nutrition_type='vegan', stays_overnight=True
                )
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        member = CrewMember.objects.get(user=self.user, crew=self.crew)
        self.assertEqual(member.nutrition, 'vegan')
        self.assertTrue(member.stays_overnight)
        self.assertEqual(member.shirt, new_shirt)

    def test_crew_signup_assigns_team_and_stores_member(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(
                _base_payload(self.shirt.id, team_ids=[str(self.event_team.id)])
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        member = CrewMember.objects.get(user=self.user, crew=self.crew)
        self.assertTrue(
            TeamMember.objects.filter(
                crewmember=member, event_team=self.event_team
            ).exists()
        )

    def test_crew_signup_rejects_invalid_team_id(self):
        """A team not belonging to this event returns 400."""
        import uuid

        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(_base_payload(self.shirt.id, team_ids=[str(uuid.uuid4())])),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload['status'], 'error')

    def test_crew_signup_rejects_invalid_team_category(self):
        """A team category not linked to this event returns 400."""
        import uuid

        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(
                _base_payload(self.shirt.id, teamcategory_ids=[str(uuid.uuid4())])
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload['status'], 'error')

    def test_crew_signup_returns_404_for_unknown_event(self):
        self.client.force_login(self.user)

        response = self.client.post(
            '/api/v2/crew-signup/no-such-event/',
            data=json.dumps(_base_payload(self.shirt.id)),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)

    def test_crew_signup_requires_authentication(self):
        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(_base_payload(self.shirt.id)),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)

    @patch('rockon.api.endpoints.crew_signup.send_mail_async')
    def test_crew_signup_sends_notification_when_crewcoord_group_has_members(
        self, send_mail_async
    ):
        from django.contrib.auth.models import Group

        group = Group.objects.create(name='crewcoord')
        notified_user = User.objects.create_user(
            username='coord',
            email='coord@example.com',
            password='secret',
        )
        group.user_set.add(notified_user)

        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(_base_payload(self.shirt.id)),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        send_mail_async.assert_called_once()
        call_kwargs = send_mail_async.call_args.kwargs
        self.assertTrue(call_kwargs['subject'].endswith('Neue Crew-Anmeldung'))
        self.assertIn(
            'es gibt eine neue Crew-Anmeldung bei Rocktreff 2026.',
            call_kwargs['message'],
        )
        self.assertIn(
            'eine neue Crew-Anmeldung bei Rocktreff 2026.',
            call_kwargs['html_message'],
        )
        self.assertIn('coord@example.com', call_kwargs['recipient_list'])

    @patch('rockon.api.endpoints.crew_signup.send_mail_async')
    def test_crew_signup_update_sends_update_notification_to_crewcoord(
        self, send_mail_async
    ):
        from django.contrib.auth.models import Group

        group = Group.objects.create(name='crewcoord')
        notified_user = User.objects.create_user(
            username='coord-update',
            email='coord-update@example.com',
            password='secret',
        )
        group.user_set.add(notified_user)
        CrewMember.objects.create(user=self.user, crew=self.crew, shirt=self.shirt)

        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(
                _base_payload(
                    self.shirt.id, nutrition_type='vegetarian', stays_overnight=True
                )
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        send_mail_async.assert_called_once()
        call_kwargs = send_mail_async.call_args.kwargs
        self.assertTrue(call_kwargs['subject'].endswith('Crew-Anmeldung aktualisiert'))
        self.assertIn(
            'eine bestehende Crew-Anmeldung bei Rocktreff 2026 wurde aktualisiert.',
            call_kwargs['message'],
        )
        normalized_html = ' '.join(call_kwargs['html_message'].split())
        self.assertIn(
            'eine bestehende Crew-Anmeldung bei Rocktreff 2026 wurde aktualisiert.',
            normalized_html,
        )
        self.assertIn('coord-update@example.com', call_kwargs['recipient_list'])

    @patch('rockon.api.endpoints.crew_signup.send_mail_async')
    def test_crew_signup_succeeds_without_crewcoord_group(self, send_mail_async):
        """Missing crewcoord group should not block signup."""
        self.client.force_login(self.user)

        response = self.client.post(
            f'/api/v2/crew-signup/{self.event.slug}/',
            data=json.dumps(_base_payload(self.shirt.id)),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        send_mail_async.assert_not_called()
