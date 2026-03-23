from __future__ import annotations

import json
from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase

from rockon.bands.models import Band, BandMedia, Track
from rockon.bands.models.band import BidStatus
from rockon.base.models import Event
from rockon.base.models.event import SignUpType


def _make_event(*, slug: str, name: str, offset_days: int = 0) -> Event:
    start = date(2026, 7, 1) + timedelta(days=offset_days)
    return Event.objects.create(
        name=name,
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


class BandEndpointTests(TestCase):
    def setUp(self):
        self.event = _make_event(slug='rocktreff-2026', name='Rocktreff 2026')
        self.other_event = _make_event(
            slug='rocktreff-2027',
            name='Rocktreff 2027',
            offset_days=365,
        )

        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='secret',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='secret',
        )
        self.crew_user = User.objects.create_user(
            username='crew',
            email='crew@example.com',
            password='secret',
        )

        crew_group, _ = Group.objects.get_or_create(name='crew')
        self.crew_user.groups.add(crew_group)

        self.track = Track.objects.create(name='Main Stage')
        self.track.events.add(self.event)

        self.band = Band.objects.create(
            event=self.event,
            contact=self.owner,
            name='The Testers',
            bid_status=BidStatus.PENDING,
            track=self.track,
        )
        self.other_band = Band.objects.create(
            event=self.other_event,
            name='Other Band',
            bid_status=BidStatus.UNKNOWN,
        )

    def test_list_requires_authentication(self):
        response = self.client.get('/api/v2/bands/')

        self.assertEqual(response.status_code, 401)

    def test_list_returns_bands_and_filters_by_event_slug(self):
        self.client.force_login(self.owner)

        response = self.client.get('/api/v2/bands/')
        self.assertEqual(response.status_code, 200)
        ids = {item['id'] for item in response.json()}
        self.assertIn(str(self.band.id), ids)
        self.assertIn(str(self.other_band.id), ids)

        response = self.client.get('/api/v2/bands/?event=rocktreff-2026')
        self.assertEqual(response.status_code, 200)
        items = response.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['id'], str(self.band.id))

    def test_get_band_returns_detail_with_media_categories(self):
        self.client.force_login(self.owner)
        BandMedia.objects.create(
            band=self.band,
            media_type='audio',
            url='https://example.com/song.mp3',
        )
        BandMedia.objects.create(
            band=self.band,
            media_type='link',
            url='https://example.com/link',
        )
        BandMedia.objects.create(
            band=self.band,
            media_type='web',
            url='https://example.com',
        )
        BandMedia.objects.create(
            band=self.band,
            media_type='document',
            url='https://example.com/tech.pdf',
        )

        response = self.client.get(f'/api/v2/bands/{self.band.id}')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['id'], str(self.band.id))
        self.assertEqual(payload['contact']['id'], self.owner.id)
        self.assertEqual(len(payload['songs']), 1)
        self.assertEqual(len(payload['links']), 1)
        self.assertEqual(len(payload['web_links']), 1)
        self.assertEqual(len(payload['documents']), 1)

    def test_patch_requires_band_access(self):
        self.client.force_login(self.other_user)

        response = self.client.patch(
            f'/api/v2/bands/{self.band.id}',
            data=json.dumps({'name': 'Unauthorized Change'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_patch_allows_owner_to_update_band_fields(self):
        self.client.force_login(self.owner)

        response = self.client.patch(
            f'/api/v2/bands/{self.band.id}',
            data=json.dumps(
                {
                    'name': 'Updated Name',
                    'genre': 'Rock',
                    'federal_state': 'berlin',
                    'cover_letter': 'Hello',
                    'are_students': True,
                    'has_management': True,
                    'mean_age_under_27': True,
                    'is_coverband': False,
                    'track': str(self.track.id),
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.band.refresh_from_db()
        self.assertEqual(self.band.name, 'Updated Name')
        self.assertEqual(self.band.genre, 'Rock')
        self.assertEqual(self.band.track_id, self.track.id)
        self.assertTrue(self.band.are_students)
        self.assertTrue(self.band.has_management)
        self.assertTrue(self.band.mean_age_under_27)

    def test_patch_bid_status_requires_booking_group(self):
        self.client.force_login(self.owner)

        response = self.client.patch(
            f'/api/v2/bands/{self.band.id}',
            data=json.dumps({'bid_status': BidStatus.ACCEPTED}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
        self.band.refresh_from_db()
        self.assertEqual(self.band.bid_status, BidStatus.PENDING)

    def test_patch_bid_status_allows_booking_group_member(self):
        booking_group, _ = Group.objects.get_or_create(name='booking')
        self.owner.groups.add(booking_group)
        self.client.force_login(self.owner)

        response = self.client.patch(
            f'/api/v2/bands/{self.band.id}',
            data=json.dumps({'bid_status': BidStatus.ACCEPTED}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.band.refresh_from_db()
        self.assertEqual(self.band.bid_status, BidStatus.ACCEPTED)

    def test_patch_allows_crew_member_without_ownership(self):
        self.client.force_login(self.crew_user)

        response = self.client.patch(
            f'/api/v2/bands/{self.band.id}',
            data=json.dumps({'name': 'Crew Updated'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.band.refresh_from_db()
        self.assertEqual(self.band.name, 'Crew Updated')

    def test_patch_returns_404_for_unknown_band(self):
        import uuid

        self.client.force_login(self.owner)
        response = self.client.patch(
            f'/api/v2/bands/{uuid.uuid4()}',
            data=json.dumps({'name': 'No Band'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)
