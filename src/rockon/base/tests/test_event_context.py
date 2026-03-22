from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch
from urllib.parse import quote

from django.contrib.auth.models import Group, User
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.base.services import get_current_event_for_request


class EventContextTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.event_one = self._create_event(
            name='Rocktreff 2025',
            slug='rt-2025',
            offset_days=0,
            is_current=True,
        )
        self.event_two = self._create_event(
            name='Rocktreff 2026',
            slug='rt-2026',
            offset_days=30,
        )
        self.sub_event_one = self._create_event(
            name='Spielfest 2025',
            slug='sf-2025',
            offset_days=1,
            parent=self.event_one,
        )
        self.sub_event_two = self._create_event(
            name='Spielfest 2026',
            slug='sf-2026',
            offset_days=31,
            parent=self.event_two,
        )
        self.staff_user = User.objects.create_user(
            username='staff-user',
            email='staff@example.com',
            password='secret',
            is_staff=True,
        )
        self.band_user = User.objects.create_user(
            username='band-user',
            email='band@example.com',
            password='secret',
        )
        self.band_group = Group.objects.create(name='bands')
        self.band_user.groups.add(self.band_group)

    def _create_event(
        self,
        *,
        name: str,
        slug: str,
        offset_days: int,
        is_current: bool = False,
        parent: Event | None = None,
    ) -> Event:
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
            is_current=is_current,
            sub_event_of=parent,
        )

    def test_current_event_uses_route_slug_and_normalizes_sub_events(self):
        path = reverse('exhibitors:join', kwargs={'slug': self.sub_event_one.slug})
        request = self.factory.get(path)
        request.user = self.staff_user
        request.resolver_match = resolve(path)

        current_event = get_current_event_for_request(request)

        self.assertEqual(current_event, self.event_one)

    def test_current_event_falls_back_without_session_on_non_event_pages(self):
        path = reverse('crm_user_home')
        request = self.factory.get(path)
        request.user = self.band_user
        request.resolver_match = resolve(path)

        current_event = get_current_event_for_request(request)

        self.assertEqual(current_event, self.event_one)

    def test_switch_event_preserves_current_view_and_query_string(self):
        self.client.force_login(self.staff_user)
        next_path = (
            reverse('crew:coord_members', kwargs={'slug': self.event_one.slug})
            + '?state=confirmed'
        )
        switch_url = reverse(
            'base:switch_event', kwargs={'event_slug': self.event_two.slug}
        )

        response = self.client.get(
            f'{switch_url}?next={quote(next_path, safe="")}&ctx=crew'
        )

        self.assertRedirects(
            response,
            reverse('crew:coord_members', kwargs={'slug': self.event_two.slug})
            + '?state=confirmed',
            fetch_redirect_response=False,
        )
        session = self.client.session
        self.assertNotIn('current_event_id', session)
        self.assertNotIn('current_event_slug', session)

    def test_switch_event_uses_matching_sub_event_for_exhibitor_routes(self):
        self.client.force_login(self.staff_user)
        next_path = (
            reverse('exhibitors:join', kwargs={'slug': self.sub_event_one.slug})
            + '?tab=assets'
        )
        switch_url = reverse(
            'base:switch_event', kwargs={'event_slug': self.event_two.slug}
        )

        response = self.client.get(
            f'{switch_url}?next={quote(next_path, safe="")}&ctx=exhibitors'
        )

        self.assertRedirects(
            response,
            reverse('exhibitors:join', kwargs={'slug': self.sub_event_two.slug})
            + '?tab=assets',
            fetch_redirect_response=False,
        )

    def test_switch_event_from_non_event_page_uses_context_default_route(self):
        self.client.force_login(self.staff_user)
        switch_url = reverse(
            'base:switch_event', kwargs={'event_slug': self.event_two.slug}
        )
        home_url = reverse('crm_user_home')

        response = self.client.get(
            f'{switch_url}?next={quote(home_url, safe="")}&ctx=bands'
        )

        self.assertRedirects(
            response,
            reverse('bands:bid_router', kwargs={'slug': self.event_two.slug}),
            fetch_redirect_response=False,
        )

    @patch('rockon.base.views.account.authenticate')
    def test_login_token_does_not_store_current_event_in_session(self, authenticate):
        authenticate.return_value = self.band_user

        response = self.client.get(
            reverse('base:login_token', kwargs={'token': 'magic-token'})
        )

        self.assertRedirects(
            response,
            reverse('bands:bid_router', kwargs={'slug': self.event_one.slug}),
            fetch_redirect_response=False,
        )
        session = self.client.session
        self.assertNotIn('current_event_id', session)
        self.assertNotIn('current_event_slug', session)
