from __future__ import annotations

import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from rockon.bands.models import Band, BandMedia
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


class BandMediaListEndpointTests(TestCase):
    def setUp(self):
        self.event = _make_event()

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
        self.staff_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='secret',
            is_staff=True,
        )

        self.band = Band.objects.create(
            event=self.event,
            contact=self.owner,
            name='Owner Band',
            bid_status=BidStatus.PENDING,
        )
        self.band.contact = self.owner
        self.band.save()
        self.owner.bands.add(self.band)

        self.other_band = Band.objects.create(
            event=self.event,
            name='Other Band',
            bid_status=BidStatus.PENDING,
        )
        self.other_user.bands.add(self.other_band)

        self.media = BandMedia.objects.create(
            band=self.band,
            media_type='audio',
            url='https://example.com/song.mp3',
        )
        self.other_media = BandMedia.objects.create(
            band=self.other_band,
            media_type='audio',
            url='https://example.com/other.mp3',
        )

    def test_list_requires_authentication(self):
        response = self.client.get('/api/v2/band-media/')

        self.assertEqual(response.status_code, 401)

    def test_list_returns_only_own_bands_media_for_non_staff(self):
        self.client.force_login(self.owner)

        response = self.client.get('/api/v2/band-media/')

        self.assertEqual(response.status_code, 200)
        ids = {item['id'] for item in response.json()}
        self.assertIn(str(self.media.id), ids)
        self.assertNotIn(str(self.other_media.id), ids)

    def test_list_returns_all_media_for_staff(self):
        self.client.force_login(self.staff_user)

        response = self.client.get('/api/v2/band-media/')

        self.assertEqual(response.status_code, 200)
        ids = {item['id'] for item in response.json()}
        self.assertIn(str(self.media.id), ids)
        self.assertIn(str(self.other_media.id), ids)

    def test_list_filters_by_band_id(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(f'/api/v2/band-media/?band_id={self.band.id}')

        self.assertEqual(response.status_code, 200)
        items = response.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['id'], str(self.media.id))


class BandMediaUploadEndpointTests(TestCase):
    def setUp(self):
        self.event = _make_event()

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
        self.band = Band.objects.create(
            event=self.event,
            name='Upload Band',
            bid_status=BidStatus.PENDING,
        )
        self.owner.bands.add(self.band)

    def test_upload_url_media_creates_entry(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            '/api/v2/band-media/upload/',
            data=json.dumps(
                {
                    'band': str(self.band.id),
                    'media_type': 'link',
                    'url': 'https://example.com/link',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload['url'], 'https://example.com/link')
        self.assertEqual(payload['media_type'], 'link')
        self.assertEqual(payload['band'], str(self.band.id))
        self.assertTrue(
            BandMedia.objects.filter(band=self.band, media_type='link').exists()
        )

    def test_upload_returns_400_when_band_missing(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            '/api/v2/band-media/upload/',
            data=json.dumps({'media_type': 'link', 'url': 'https://example.com'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_upload_rejected_for_non_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            '/api/v2/band-media/upload/',
            data=json.dumps(
                {
                    'band': str(self.band.id),
                    'media_type': 'link',
                    'url': 'https://example.com',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_upload_requires_authentication(self):
        response = self.client.post(
            '/api/v2/band-media/upload/',
            data=json.dumps(
                {
                    'band': str(self.band.id),
                    'media_type': 'link',
                    'url': 'https://example.com',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)

    def test_staff_can_upload_for_any_band(self):
        staff = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='secret',
            is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.post(
            '/api/v2/band-media/upload/',
            data=json.dumps(
                {
                    'band': str(self.band.id),
                    'media_type': 'web',
                    'url': 'https://example.com/website',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)


class BandMediaDeleteEndpointTests(TestCase):
    def setUp(self):
        self.event = _make_event()

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
        self.staff_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='secret',
            is_staff=True,
        )
        self.band = Band.objects.create(
            event=self.event,
            name='Media Band',
            bid_status=BidStatus.PENDING,
        )
        self.owner.bands.add(self.band)
        self.media = BandMedia.objects.create(
            band=self.band,
            media_type='audio',
            url='https://example.com/song.mp3',
        )

    def test_delete_media_as_owner(self):
        self.client.force_login(self.owner)

        response = self.client.delete(f'/api/v2/band-media/{self.media.id}/')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(BandMedia.objects.filter(id=self.media.id).exists())

    def test_delete_media_returns_403_for_non_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.delete(f'/api/v2/band-media/{self.media.id}/')

        self.assertEqual(response.status_code, 403)
        self.assertTrue(BandMedia.objects.filter(id=self.media.id).exists())

    def test_delete_media_as_staff(self):
        self.client.force_login(self.staff_user)

        response = self.client.delete(f'/api/v2/band-media/{self.media.id}/')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(BandMedia.objects.filter(id=self.media.id).exists())

    def test_delete_returns_404_for_unknown_media(self):
        import uuid

        self.client.force_login(self.owner)
        response = self.client.delete(f'/api/v2/band-media/{uuid.uuid4()}/')

        self.assertEqual(response.status_code, 404)
