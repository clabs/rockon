from __future__ import annotations

import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from rockon.bands.models import Band, BandMember
from rockon.bands.models.band import BidStatus
from rockon.base.models import Event
from rockon.base.models.event import SignUpType


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


def _person_payload(**kwargs) -> dict:
    defaults = {
        'first_name': 'Hans',
        'last_name': 'Drummer',
        'email': 'hans-drummer@example.com',
        'address': 'Musterstrasse',
        'housenumber': '1',
        'zip_code': '10115',
        'place': 'Berlin',
        'nutrition': 'omnivore',
        'position': 'drums',
    }
    defaults.update(kwargs)
    return defaults


class BandMemberSignupEndpointTests(TestCase):
    def setUp(self):
        self.event = _make_event()
        self.user = User.objects.create_user(
            username='bandlead',
            email='bandlead@example.com',
            password='secret',
        )
        self.band = Band.objects.create(
            event=self.event,
            name='The Testers',
            bid_status=BidStatus.PENDING,
            contact=self.user,
        )
        self.client.force_login(self.user)

    def test_signup_creates_band_members(self):
        response = self.client.post(
            '/api/v2/bandmember-signup/',
            data=json.dumps(
                {
                    'band': str(self.band.id),
                    'persons': [_person_payload()],
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'status': 'ok', 'message': 'Entries done.'},
        )
        self.assertEqual(BandMember.objects.filter(band=self.band).count(), 1)
        member = BandMember.objects.get(band=self.band)
        self.assertEqual(member.user.first_name, 'Hans')
        self.assertEqual(member.user.email, 'hans-drummer@example.com')

    def test_signup_creates_alias_for_existing_email(self):
        """If a user with the same email exists, an alias account is created."""
        User.objects.create_user(
            username='hans-drummer@example.com',
            email='hans-drummer@example.com',
            password='secret',
            first_name='Existing',
            last_name='User',
        )

        response = self.client.post(
            '/api/v2/bandmember-signup/',
            data=json.dumps(
                {
                    'band': str(self.band.id),
                    'persons': [_person_payload()],
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        # The new member's user should have an aliased email, not the original
        member = BandMember.objects.get(band=self.band)
        self.assertNotEqual(member.user.email, 'hans-drummer@example.com')
        self.assertTrue(member.user.email.endswith('@rockon.dev'))

    def test_signup_stops_at_10_members(self):
        """No additional members are created once the band already has 10."""
        # Pre-populate 10 existing members so the limit check fires immediately
        for i in range(10):
            user = User.objects.create_user(
                username=f'pre{i}@example.com',
                email=f'pre{i}@example.com',
            )
            BandMember.objects.create(band=self.band, user=user)

        response = self.client.post(
            '/api/v2/bandmember-signup/',
            data=json.dumps(
                {
                    'band': str(self.band.id),
                    'persons': [_person_payload(email='extra@example.com')],
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(BandMember.objects.filter(band=self.band).count(), 10)

    def test_signup_returns_404_for_unknown_band(self):
        import uuid

        response = self.client.post(
            '/api/v2/bandmember-signup/',
            data=json.dumps(
                {
                    'band': str(uuid.uuid4()),
                    'persons': [_person_payload()],
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)
