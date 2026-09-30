from __future__ import annotations

import json
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rockon.bands.models import Band, BandMedia, BandProfile, MediaType
from rockon.bands.models.band import BidStatus
from rockon.bands.services.bids import start_bid
from rockon.base.models import Event, PasskeyCredential
from rockon.base.models.event import SignUpType
from rockon.base.services import (
    calculate_available_event_ids,
    get_open_application_event,
)


def _make_event(year: int, *, is_current: bool, application_open: bool) -> Event:
    start = date(year, 7, 1)
    now = timezone.now()
    if application_open:
        window = (now - timedelta(days=1), now + timedelta(days=1))
    else:
        window = (now - timedelta(days=300), now - timedelta(days=200))
    return Event.objects.create(
        name=f'Rocktreff {year}',
        slug=f'rocktreff-{year}',
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
        is_current=is_current,
        band_application_start=window[0],
        band_application_end=window[1],
    )


class BandReapplyTestCase(TestCase):
    """Running year is still `is_current` while next year's application is open."""

    def setUp(self):
        self.last_year = _make_event(2026, is_current=True, application_open=False)
        self.next_year = _make_event(2027, is_current=False, application_open=True)
        self.user = User.objects.create_user(
            username='band-contact', email='band@example.com', password='secret'
        )
        self.user.groups.add(Group.objects.create(name='bands'))
        self.legacy_bid = Band.objects.create(
            event=self.last_year,
            contact=self.user,
            name='Nachtbaden',
            bid_status=BidStatus.LINEUP,
        )


class OpenApplicationEventTests(BandReapplyTestCase):
    def test_returns_event_with_open_window_regardless_of_is_current(self):
        self.assertEqual(get_open_application_event(), self.next_year)

    def test_returns_none_when_no_window_is_open(self):
        self.next_year.delete()

        self.assertIsNone(get_open_application_event())

    def test_band_contact_can_access_open_and_own_bid_events(self):
        available = calculate_available_event_ids(self.user)

        self.assertIn(self.next_year.id, available)
        self.assertIn(self.last_year.id, available)


class ReapplyFlowTests(BandReapplyTestCase):
    @patch('rockon.bands.views.bid.sentry_sdk.metrics.count')
    def test_bid_router_creates_new_bid_for_next_year(self, count):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('bands:bid_router', kwargs={'slug': self.next_year.slug})
        )

        new_bid = Band.objects.get(contact=self.user, event=self.next_year)
        self.assertRedirects(
            response,
            reverse(
                'bands:bid_form',
                kwargs={'slug': self.next_year.slug, 'guid': new_bid.guid},
            ),
            fetch_redirect_response=False,
        )
        count.assert_called_once()

    @patch('rockon.base.views.account.authenticate')
    def test_login_token_sends_band_user_to_open_application_event(self, authenticate):
        authenticate.return_value = self.user
        PasskeyCredential.objects.create(
            user=self.user, credential_id='cred', public_key=b''
        )

        response = self.client.get(
            reverse('base:login_token', kwargs={'token': 'magic-token'})
        )

        self.assertRedirects(
            response,
            reverse('bands:bid_router', kwargs={'slug': self.next_year.slug}),
            fetch_redirect_response=False,
        )

    def test_bid_closed_links_to_open_event_instead_of_old_members_page(self):
        self.legacy_bid.save()  # assigns slug, needed for the members redirect
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('bands:bid_closed', kwargs={'slug': self.last_year.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('bands:bid_router', kwargs={'slug': self.next_year.slug}),
        )

    def test_bid_closed_redirects_lineup_band_when_nothing_is_open(self):
        self.next_year.delete()
        self.legacy_bid.save()
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('bands:bid_closed', kwargs={'slug': self.last_year.slug})
        )

        self.assertRedirects(
            response,
            reverse(
                'bands:bands_members',
                kwargs={
                    'slug': self.last_year.slug,
                    'slug_guid': self.legacy_bid.slug,
                },
            ),
            fetch_redirect_response=False,
        )

    def test_bid_router_tolerates_duplicate_legacy_bids(self):
        Band.objects.create(event=self.next_year, contact=self.user)
        Band.objects.create(event=self.next_year, contact=self.user)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('bands:bid_router', kwargs={'slug': self.next_year.slug})
        )

        self.assertEqual(response.status_code, 302)


class StartBidServiceTests(BandReapplyTestCase):
    def test_first_bid_after_legacy_gets_fresh_profile_without_prefill(self):
        band, created = start_bid(self.user, self.next_year)

        self.assertTrue(created)
        self.assertIsNotNone(band.profile)
        self.assertEqual(band.profile.owner, self.user)
        self.assertIsNone(band.name)
        self.assertFalse(band.repeated)
        self.legacy_bid.refresh_from_db()
        self.assertIsNone(self.legacy_bid.profile)

    def test_returns_existing_bid(self):
        first, _ = start_bid(self.user, self.next_year)

        second, created = start_bid(self.user, self.next_year)

        self.assertFalse(created)
        self.assertEqual(first, second)

    def test_next_cycle_reuses_profile_and_prefills_identity_only(self):
        bid_2027, _ = start_bid(self.user, self.next_year)
        bid_2027.name = 'Nachtbaden'
        bid_2027.genre = 'Indie'
        bid_2027.federal_state = 'BE'
        bid_2027.is_flinta = True
        bid_2027.cover_letter = 'Wir wollen 2027 spielen.'
        bid_2027.bid_status = BidStatus.DECLINED
        bid_2027.save()
        BandMedia.objects.create(
            band=bid_2027, media_type=MediaType.WEB, url='https://band.example'
        )
        BandMedia.objects.create(
            band=bid_2027, media_type=MediaType.LOGO, file='bids/x/logo.png'
        )
        BandMedia.objects.create(
            band=bid_2027, media_type=MediaType.AUDIO, file='bids/x/song.mp3'
        )
        event_2028 = _make_event(2028, is_current=False, application_open=True)

        bid_2028, created = start_bid(self.user, event_2028)

        self.assertTrue(created)
        self.assertEqual(bid_2028.profile, bid_2027.profile)
        self.assertTrue(bid_2028.repeated)
        self.assertEqual(bid_2028.name, 'Nachtbaden')
        self.assertEqual(bid_2028.genre, 'Indie')
        self.assertEqual(bid_2028.federal_state, 'BE')
        self.assertTrue(bid_2028.is_flinta)
        self.assertIsNone(bid_2028.cover_letter)
        self.assertEqual(bid_2028.bid_status, BidStatus.UNKNOWN)
        self.assertEqual(
            sorted(bid_2028.media.values_list('media_type', flat=True)),
            [MediaType.LOGO, MediaType.WEB],
        )
        self.assertEqual(
            bid_2028.media.get(media_type=MediaType.LOGO).file.name,
            'bids/x/logo.png',
        )

    def test_profile_allows_only_one_bid_per_event(self):
        band, _ = start_bid(self.user, self.next_year)

        with self.assertRaises(IntegrityError):
            Band.objects.create(
                event=self.next_year, contact=self.user, profile=band.profile
            )


class ProfileNameSyncTests(BandReapplyTestCase):
    def test_patching_latest_bid_name_updates_profile(self):
        band, _ = start_bid(self.user, self.next_year)
        self.client.force_login(self.user)

        response = self.client.patch(
            f'/api/v2/bands/{band.id}',
            data=json.dumps({'name': 'Nachtbaden'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(BandProfile.objects.get(id=band.profile_id).name, 'Nachtbaden')
