from __future__ import annotations

import json
from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase

from rockon.bands.models import Band, Stage, TimeSlot, Track
from rockon.bands.models.band import BidStatus
from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import Attendance


class TimeSlotCommentTrackEndpointsTests(TestCase):
    def setUp(self):
        self.booking_group = Group.objects.create(name='booking')
        self.booking_user = User.objects.create_user(
            username='booking-user',
            email='booking@example.com',
            password='secret',
            first_name='Book',
            last_name='Ing',
        )
        self.booking_user.groups.add(self.booking_group)

        self.regular_user = User.objects.create_user(
            username='regular-user',
            email='regular@example.com',
            password='secret',
            first_name='Regular',
            last_name='User',
        )

        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026', 0)
        self.event_two = self._create_event('Rocktreff 2027', 'rocktreff-2027', 30)

        self.attendance = Attendance.objects.create(
            event=self.event,
            day=self.event.start,
            phase='show',
        )
        self.stage = Stage.objects.create(event=self.event, name='Main Stage')

        self.timeslot = TimeSlot.objects.create(
            stage=self.stage,
            day=self.attendance,
            start=time(18, 0),
            end=time(19, 0),
        )
        self.timeslot_other = TimeSlot.objects.create(
            stage=self.stage,
            day=self.attendance,
            start=time(20, 0),
            end=time(21, 0),
        )

        self.track_active = Track.objects.create(name='Rock', slug='rock', active=True)
        self.track_active.events.add(self.event)
        self.track_other_event = Track.objects.create(
            name='Alt', slug='alt', active=True
        )
        self.track_other_event.events.add(self.event_two)
        self.track_inactive = Track.objects.create(
            name='Hidden',
            slug='hidden',
            active=False,
        )

        self.band_lineup = Band.objects.create(
            event=self.event,
            name='Lineup Band',
            bid_status=BidStatus.LINEUP,
            track=self.track_active,
        )
        self.band_replacement = Band.objects.create(
            event=self.event,
            name='Replacement Band',
            bid_status=BidStatus.REPLACEMENT,
            track=self.track_active,
        )
        self.band_pending = Band.objects.create(
            event=self.event,
            name='Pending Band',
            bid_status=BidStatus.PENDING,
            track=self.track_active,
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

    def test_timeslot_list_requires_booking_group(self):
        self.client.force_login(self.regular_user)

        response = self.client.get('/api/v2/timeslots/')

        self.assertEqual(response.status_code, 403)

    def test_timeslot_list_filters_by_event(self):
        self.client.force_login(self.booking_user)

        response = self.client.get(f'/api/v2/timeslots/?event={self.event.slug}')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]['stage_name'], 'Main Stage')
        self.assertEqual(payload[0]['day'], self.event.start.isoformat())

    def test_timeslot_patch_assigns_band_and_clears_previous_slot(self):
        self.client.force_login(self.booking_user)
        self.timeslot_other.band = self.band_lineup
        self.timeslot_other.save(update_fields=['band'])

        response = self.client.patch(
            f'/api/v2/timeslots/{self.timeslot.id}/',
            data=json.dumps({'band_id': str(self.band_lineup.id)}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.timeslot.refresh_from_db()
        self.timeslot_other.refresh_from_db()
        self.assertEqual(self.timeslot.band_id, self.band_lineup.id)
        self.assertIsNone(self.timeslot_other.band_id)

    def test_timeslot_patch_rejects_non_lineup_status(self):
        self.client.force_login(self.booking_user)

        response = self.client.patch(
            f'/api/v2/timeslots/{self.timeslot.id}/',
            data=json.dumps({'band_id': str(self.band_pending.id)}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)

    def test_timeslot_patch_can_clear_band(self):
        self.client.force_login(self.booking_user)
        self.timeslot.band = self.band_replacement
        self.timeslot.save(update_fields=['band'])

        response = self.client.patch(
            f'/api/v2/timeslots/{self.timeslot.id}/',
            data=json.dumps({'band_id': None}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.timeslot.refresh_from_db()
        self.assertIsNone(self.timeslot.band_id)

    def test_comment_create_and_list(self):
        self.client.force_login(self.regular_user)

        create_response = self.client.post(
            '/api/v2/comments/',
            data=json.dumps(
                {
                    'band': str(self.band_lineup.id),
                    'text': 'Great live performance',
                    'reason': 'stage presence',
                    'mood': 'positive',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(create_response.status_code, 201)
        payload = create_response.json()
        self.assertEqual(payload['band'], str(self.band_lineup.id))
        self.assertEqual(payload['user']['first_name'], 'Regular')

        list_response = self.client.get(f'/api/v2/comments/?band={self.band_lineup.id}')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

    def test_comment_list_rejects_invalid_band_uuid(self):
        self.client.force_login(self.regular_user)

        response = self.client.get('/api/v2/comments/?band=invalid-uuid')

        self.assertEqual(response.status_code, 400)

    def test_track_list_returns_only_active_tracks_and_filters_by_event(self):
        self.client.force_login(self.regular_user)

        response = self.client.get('/api/v2/tracks/')
        self.assertEqual(response.status_code, 200)
        slugs = {item['slug'] for item in response.json()}
        self.assertIn('rock', slugs)
        self.assertIn('alt', slugs)
        self.assertNotIn('hidden', slugs)

        filtered = self.client.get(f'/api/v2/tracks/?event={self.event.slug}')
        self.assertEqual(filtered.status_code, 200)
        filtered_slugs = {item['slug'] for item in filtered.json()}
        self.assertEqual(filtered_slugs, {'rock'})

    def test_track_list_requires_authentication(self):
        response = self.client.get('/api/v2/tracks/')

        self.assertEqual(response.status_code, 401)

    def test_comment_list_requires_authentication(self):
        response = self.client.get('/api/v2/comments/')

        self.assertEqual(response.status_code, 401)
