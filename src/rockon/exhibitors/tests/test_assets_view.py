from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event, Organisation
from rockon.base.models.event import SignUpType
from rockon.exhibitors.models import (
    Asset,
    Attendance,
    Exhibitor,
    ExhibitorAsset,
    ExhibitorAttendance,
    ExhibitorStatus,
)


class ExhibitorAssetsViewTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='exhibitor_admins')
        self.user = User.objects.create_user(
            username='exhi-admin',
            password='secret',
        )
        self.user.groups.add(self.group)
        start = date(2026, 7, 1)
        self.event = Event.objects.create(
            name='Rocktreff 2026',
            slug='rocktreff-2026',
            description='Test',
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
        self.org = Organisation.objects.create(org_name='Test Org')
        self.exhibitor = Exhibitor.objects.create(
            event=self.event,
            organisation=self.org,
            state=ExhibitorStatus.CONFIRMED,
        )

    def _url(self, slug=None):
        return reverse(
            'exhibitors:exhibitor_assets',
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

    def test_get_renders_exhibitors_with_days_and_assets(self):
        day = Attendance.objects.create(event=self.event, day=self.event.start)
        asset = Asset.objects.create(name='Strom', is_bool=True)
        ExhibitorAttendance.objects.create(exhibitor=self.exhibitor, day=day, count=3)
        ExhibitorAsset.objects.create(exhibitor=self.exhibitor, asset=asset, count=1)

        self.client.force_login(self.user)
        response = self.client.get(self._url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Org')
        self.assertContains(response, 'Strom')
        self.assertContains(response, '✓')
        self.assertContains(response, 'Gesamt')
        self.assertContains(response, 'Summe Anwesenheit')

    def test_get_renders_empty_state(self):
        Exhibitor.objects.all().delete()
        self.client.force_login(self.user)
        response = self.client.get(self._url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keine Aussteller')

    def test_unselected_asset_shows_dash(self):
        Asset.objects.create(name='Wasser', is_bool=False)

        self.client.force_login(self.user)
        response = self.client.get(self._url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wasser')
        self.assertContains(response, '–')
