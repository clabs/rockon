from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rockon.bands.models import Band
from rockon.bands.views.bid import _can_vote_on_bands
from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import Crew, CrewMember, CrewMemberStatus


class BidViewTests(TestCase):
    def setUp(self):
        self.crew_group = Group.objects.create(name='crew')
        self.booking_group = Group.objects.create(name='booking')

        self.booking_user = User.objects.create_user(
            username='booking-user',
            email='booking@example.com',
            password='secret',
        )
        self.booking_user.groups.add(self.booking_group)

        self.crew_user = User.objects.create_user(
            username='crew-user',
            email='crew@example.com',
            password='secret',
        )
        self.crew_user.groups.add(self.crew_group)

        self.other_user = User.objects.create_user(
            username='other-user',
            email='other@example.com',
            password='secret',
        )

        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026', 0)
        self.crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)

    def _create_event(self, name: str, slug: str, offset_days: int) -> Event:
        start = date(2026, 7, 1) + timedelta(days=offset_days)
        now = timezone.now()
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
            band_application_start=now - timedelta(days=1),
            band_application_end=now + timedelta(days=1),
            bid_vote_allowed=True,
            bid_browsing_allowed=True,
        )

    def test_can_vote_on_bands_requires_booking_or_confirmed_crew_member(self):
        allowed, message = _can_vote_on_bands(self.other_user, self.event)

        self.assertFalse(allowed)
        self.assertIn('nicht berechtigt', message)

    def test_can_vote_on_bands_blocks_confirmed_crew_when_browsing_is_closed(self):
        CrewMember.objects.create(
            user=self.crew_user,
            crew=self.crew,
            state=CrewMemberStatus.CONFIRMED,
        )
        self.event.bid_browsing_allowed = False
        self.event.save(update_fields=['bid_browsing_allowed'])

        allowed, message = _can_vote_on_bands(self.crew_user, self.event)

        self.assertFalse(allowed)
        self.assertEqual(message, 'Die Bandbewertung ist für dieses Event nicht aktiv.')

    def test_can_vote_on_bands_allows_booking_when_browsing_is_closed(self):
        self.event.bid_browsing_allowed = False
        self.event.save(update_fields=['bid_browsing_allowed'])

        allowed, message = _can_vote_on_bands(self.booking_user, self.event)

        self.assertTrue(allowed)
        self.assertIsNone(message)

    def test_bid_router_redirects_anonymous_users_to_login(self):
        response = self.client.get(
            reverse('bands:bid_router', kwargs={'slug': self.event.slug})
        )

        self.assertRedirects(
            response,
            f'{reverse("base:login_request")}?ctx=bands',
            fetch_redirect_response=False,
        )

    def test_bid_router_creates_band_for_authenticated_user(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse('bands:bid_router', kwargs={'slug': self.event.slug})
        )

        band = Band.objects.get(contact=self.other_user, event=self.event)
        self.assertRedirects(
            response,
            reverse(
                'bands:bid_form',
                kwargs={'slug': self.event.slug, 'guid': band.guid},
            ),
            fetch_redirect_response=False,
        )

    def test_bid_router_reuses_existing_band_for_authenticated_user(self):
        band = Band.objects.create(event=self.event, contact=self.other_user)
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse('bands:bid_router', kwargs={'slug': self.event.slug})
        )

        self.assertEqual(
            Band.objects.filter(contact=self.other_user, event=self.event).count(),
            1,
        )
        self.assertRedirects(
            response,
            reverse(
                'bands:bid_form',
                kwargs={'slug': self.event.slug, 'guid': band.guid},
            ),
            fetch_redirect_response=False,
        )

    def test_bid_form_returns_403_for_band_owned_by_another_user(self):
        band = Band.objects.create(event=self.event, contact=self.other_user)
        self.client.force_login(self.crew_user)

        response = self.client.get(
            reverse(
                'bands:bid_form',
                kwargs={'slug': self.event.slug, 'guid': band.guid},
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertContains(
            response,
            'Diese Bandbewerbung gehört nicht zu deinem Account',
            status_code=403,
        )
