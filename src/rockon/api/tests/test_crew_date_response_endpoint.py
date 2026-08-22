from __future__ import annotations

import json
from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import Crew, CrewDate, CrewDateResponse, CrewMember


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


class CrewDateResponseEndpointTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rsvp-user',
            email='rsvp@example.com',
            password='secret',
            first_name='RSVP',
            last_name='User',
        )
        self.event = _make_event()
        self.crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)
        self.crew_date = CrewDate.objects.create(
            crew=self.crew,
            title='Aufbau-Meeting',
            description='Besprechung zum Aufbau',
            date=date(2026, 6, 20),
            start_time=time(18, 0),
            end_time=time(19, 0),
        )

    def _make_confirmed_member(self) -> CrewMember:
        return CrewMember.objects.create(
            user=self.user, crew=self.crew, state='confirmed'
        )

    def test_get_response_returns_204_when_none_exists(self):
        self._make_confirmed_member()
        self.client.force_login(self.user)

        response = self.client.get(f'/api/v2/crew-date-responses/{self.crew_date.id}')

        self.assertEqual(response.status_code, 204)

    def test_get_response_returns_200_with_existing_response(self):
        self._make_confirmed_member()
        CrewDateResponse.objects.create(
            crew_date=self.crew_date, user=self.user, status='attending'
        )
        self.client.force_login(self.user)

        response = self.client.get(f'/api/v2/crew-date-responses/{self.crew_date.id}')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['crew_date'], str(self.crew_date.id))
        self.assertEqual(payload['status'], 'attending')

    def test_get_response_requires_authentication(self):
        response = self.client.get(f'/api/v2/crew-date-responses/{self.crew_date.id}')

        self.assertEqual(response.status_code, 401)

    def test_submit_response_creates_new_response(self):
        self._make_confirmed_member()
        self.client.force_login(self.user)

        response = self.client.patch(
            '/api/v2/crew-date-responses/',
            data=json.dumps(
                {'crew_date': str(self.crew_date.id), 'status': 'tentative'}
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            CrewDateResponse.objects.get(
                crew_date=self.crew_date, user=self.user
            ).status,
            'tentative',
        )

    def test_submit_response_updates_existing_response(self):
        self._make_confirmed_member()
        CrewDateResponse.objects.create(
            crew_date=self.crew_date, user=self.user, status='attending'
        )
        self.client.force_login(self.user)

        response = self.client.patch(
            '/api/v2/crew-date-responses/',
            data=json.dumps(
                {'crew_date': str(self.crew_date.id), 'status': 'unavailable'}
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            CrewDateResponse.objects.get(
                crew_date=self.crew_date, user=self.user
            ).status,
            'unavailable',
        )

    def test_submit_response_rejects_invalid_status(self):
        self._make_confirmed_member()
        self.client.force_login(self.user)

        response = self.client.patch(
            '/api/v2/crew-date-responses/',
            data=json.dumps({'crew_date': str(self.crew_date.id), 'status': 'maybe'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_submit_response_rejects_non_crew_member(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            '/api/v2/crew-date-responses/',
            data=json.dumps(
                {'crew_date': str(self.crew_date.id), 'status': 'attending'}
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            CrewDateResponse.objects.filter(
                crew_date=self.crew_date, user=self.user
            ).exists()
        )

    def test_submit_response_returns_404_for_unknown_crew_date(self):
        self._make_confirmed_member()
        self.client.force_login(self.user)
        import uuid

        response = self.client.patch(
            '/api/v2/crew-date-responses/',
            data=json.dumps({'crew_date': str(uuid.uuid4()), 'status': 'attending'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)

    def test_submit_response_requires_authentication(self):
        response = self.client.patch(
            '/api/v2/crew-date-responses/',
            data=json.dumps(
                {'crew_date': str(self.crew_date.id), 'status': 'attending'}
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
