from __future__ import annotations

import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from rockon.bands.models import Band, BandVote
from rockon.bands.models.band import BidStatus
from rockon.base.models import Event
from rockon.base.models.event import SignUpType


class BandVoteEndpointTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='voter',
            email='voter@example.com',
            password='secret',
            first_name='Vote',
            last_name='Er',
        )
        start = date(2026, 7, 1)
        self.event = Event.objects.create(
            name='Rocktreff 2026',
            slug='rocktreff-2026',
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
        self.band = Band.objects.create(
            event=self.event,
            name='Test Band',
            bid_status=BidStatus.PENDING,
        )

    def test_get_vote_returns_204_when_no_vote_exists(self):
        self.client.force_login(self.user)

        response = self.client.get(f'/api/v2/band-votes/{self.band.id}')

        self.assertEqual(response.status_code, 204)

    def test_get_vote_returns_200_with_existing_vote(self):
        self.client.force_login(self.user)
        BandVote.objects.create(
            band=self.band,
            user=self.user,
            event=self.event,
            vote=3,
        )

        response = self.client.get(f'/api/v2/band-votes/{self.band.id}')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['band'], str(self.band.id))
        self.assertEqual(payload['vote'], 3)

    def test_get_vote_requires_authentication(self):
        response = self.client.get(f'/api/v2/band-votes/{self.band.id}')

        self.assertEqual(response.status_code, 401)

    def test_submit_vote_creates_new_vote(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            '/api/v2/band-votes/',
            data=json.dumps({'band': str(self.band.id), 'vote': 4}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            BandVote.objects.filter(band=self.band, user=self.user, vote=4).exists()
        )

    def test_submit_vote_updates_existing_vote(self):
        self.client.force_login(self.user)
        BandVote.objects.create(
            band=self.band,
            user=self.user,
            event=self.event,
            vote=2,
        )

        response = self.client.patch(
            '/api/v2/band-votes/',
            data=json.dumps({'band': str(self.band.id), 'vote': 5}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(BandVote.objects.get(band=self.band, user=self.user).vote, 5)

    def test_submit_vote_minus1_removes_existing_vote(self):
        self.client.force_login(self.user)
        BandVote.objects.create(
            band=self.band,
            user=self.user,
            event=self.event,
            vote=3,
        )

        response = self.client.patch(
            '/api/v2/band-votes/',
            data=json.dumps({'band': str(self.band.id), 'vote': -1}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            BandVote.objects.filter(band=self.band, user=self.user).exists()
        )

    def test_submit_vote_returns_404_for_unknown_band(self):
        self.client.force_login(self.user)
        import uuid

        response = self.client.patch(
            '/api/v2/band-votes/',
            data=json.dumps({'band': str(uuid.uuid4()), 'vote': 3}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)

    def test_submit_vote_requires_authentication(self):
        response = self.client.patch(
            '/api/v2/band-votes/',
            data=json.dumps({'band': str(self.band.id), 'vote': 3}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
