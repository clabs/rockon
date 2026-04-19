from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event, Organisation
from rockon.base.models.event import SignUpType
from rockon.exhibitors.models import Exhibitor, ExhibitorStatus


class ExhibitorListViewTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='exhibitor_admins')
        self.user = User.objects.create_user(
            username='exhi-admin',
            password='secret',
        )
        self.user.groups.add(self.group)
        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026')
        self.org = Organisation.objects.create(org_name='Test Org')
        self.exhibitor = Exhibitor.objects.create(
            event=self.event,
            organisation=self.org,
            state=ExhibitorStatus.UNKNOWN,
        )

    def _create_event(self, name, slug):
        start = date(2026, 7, 1)
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
            signup_type=SignUpType.EXHIBITOR,
            signup_is_open=True,
        )

    def _url(self, slug=None):
        return reverse(
            'exhibitors:exhibitor_list',
            kwargs={'slug': slug or self.event.slug},
        )

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 302)

    def test_user_without_group_is_redirected(self):
        user = User.objects.create_user(username='regular', password='secret')
        self.client.force_login(user)

        response = self.client.get(self._url())

        self.assertEqual(response.status_code, 302)

    def test_returns_404_for_unknown_slug(self):
        self.client.force_login(self.user)

        response = self.client.get(self._url(slug='nonexistent'))

        self.assertEqual(response.status_code, 404)

    def test_get_renders_exhibitor_list(self):
        self.client.force_login(self.user)

        response = self.client.get(self._url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Org')
        self.assertContains(response, 'Aussteller')

    def test_get_filters_by_state(self):
        org2 = Organisation.objects.create(org_name='Confirmed Org')
        Exhibitor.objects.create(
            event=self.event,
            organisation=org2,
            state=ExhibitorStatus.CONFIRMED,
        )
        self.client.force_login(self.user)

        response = self.client.get(self._url(), {'state': 'confirmed'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirmed Org')
        self.assertNotContains(response, 'Test Org')

    def test_get_filters_by_search_query(self):
        org2 = Organisation.objects.create(org_name='Another Org')
        Exhibitor.objects.create(
            event=self.event,
            organisation=org2,
            state=ExhibitorStatus.UNKNOWN,
        )
        self.client.force_login(self.user)

        response = self.client.get(self._url(), {'q': 'Another'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Another Org')
        self.assertNotContains(response, 'Test Org')

    def test_post_updates_exhibitor_state(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self._url(),
            {
                'action': 'update_exhibitor_state',
                'exhibitor_id': str(self.exhibitor.id),
                'state': ExhibitorStatus.CONFIRMED,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.exhibitor.refresh_from_db()
        self.assertEqual(self.exhibitor.state, ExhibitorStatus.CONFIRMED)

    def test_post_invalid_state_shows_error(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self._url(),
            {
                'action': 'update_exhibitor_state',
                'exhibitor_id': str(self.exhibitor.id),
                'state': 'invalid_state',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ungültiger Status.')
        self.exhibitor.refresh_from_db()
        self.assertEqual(self.exhibitor.state, ExhibitorStatus.UNKNOWN)

    def test_post_invalid_exhibitor_shows_error(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self._url(),
            {
                'action': 'update_exhibitor_state',
                'exhibitor_id': '00000000-0000-0000-0000-000000000000',
                'state': ExhibitorStatus.CONFIRMED,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ungültiger Aussteller')

    def test_post_unknown_action_shows_error(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self._url(),
            {'action': 'bogus'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unbekannte Aktion.')

    def test_post_preserves_filter_params_in_redirect(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self._url(),
            {
                'action': 'update_exhibitor_state',
                'exhibitor_id': str(self.exhibitor.id),
                'state': ExhibitorStatus.CONTACTED,
                'q': 'Test',
                'state_filter': 'contacted',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('q=Test', response.url)
        self.assertIn('state=contacted', response.url)

    def test_post_updates_market_id_with_digits(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self._url(),
            {
                'action': 'update_market_id',
                'exhibitor_id': str(self.exhibitor.id),
                'market_id': '12345',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.exhibitor.refresh_from_db()
        self.assertEqual(self.exhibitor.market_id, '12345')

    def test_post_rejects_market_id_with_non_digits(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self._url(),
            {
                'action': 'update_market_id',
                'exhibitor_id': str(self.exhibitor.id),
                'market_id': 'A12',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Markt-ID darf nur Ziffern enthalten.')
        self.exhibitor.refresh_from_db()
        self.assertIsNone(self.exhibitor.market_id)

    def test_post_rejects_duplicate_market_id(self):
        other_org = Organisation.objects.create(org_name='Other Org')
        Exhibitor.objects.create(
            event=self.event,
            organisation=other_org,
            state=ExhibitorStatus.UNKNOWN,
            market_id='999',
        )
        self.client.force_login(self.user)

        response = self.client.post(
            self._url(),
            {
                'action': 'update_market_id',
                'exhibitor_id': str(self.exhibitor.id),
                'market_id': '999',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Diese Markt-ID ist bereits vergeben.')
        self.exhibitor.refresh_from_db()
        self.assertIsNone(self.exhibitor.market_id)
