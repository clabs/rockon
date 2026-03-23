from __future__ import annotations

import json
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase

from rockon.base.models import Event
from rockon.base.models.organisation import Organisation
from rockon.base.models.event import SignUpType
from rockon.exhibitors.models import Attendance, Asset, Exhibitor


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


def _base_payload(**kwargs) -> dict:
    defaults = {
        'organisation_name': 'Testverein',
        'organisation_address': 'Musterstrasse',
        'organisation_address_housenumber': '1',
        'organisation_address_extension': '',
        'organisation_zip': '10115',
        'organisation_place': 'Berlin',
        'attendances': [],
        'assets': [],
        'offer_note': 'We sell things.',
        'general_note': '',
        'website': 'https://testverein.example.com',
    }
    defaults.update(kwargs)
    return defaults


def _post(client, url, payload):
    """Submit as multipart FormData with 'data' JSON field (mirrors JS FormData)."""
    return client.post(url, data={'data': json.dumps(payload)})


class ExhibitorSignupEndpointTests(TestCase):
    def setUp(self):
        self.event = _make_event()
        self.user = User.objects.create_user(
            username='exhibitor',
            email='exhibitor@example.com',
            password='secret',
        )
        group, _ = Group.objects.get_or_create(name='exhibitors')
        self.user.groups.add(group)

        self.attendance = Attendance.objects.create(
            event=self.event, day=date(2026, 7, 1)
        )
        self.asset = Asset.objects.create(name='Table', description='A table')

    def test_signup_requires_authentication(self):
        response = _post(
            self.client,
            f'/api/v2/exhibitor-signup/{self.event.slug}/',
            _base_payload(),
        )

        self.assertEqual(response.status_code, 401)

    def test_signup_requires_exhibitors_group(self):
        non_member = User.objects.create_user(
            username='nope',
            email='nope@example.com',
            password='secret',
        )
        self.client.force_login(non_member)

        response = _post(
            self.client,
            f'/api/v2/exhibitor-signup/{self.event.slug}/',
            _base_payload(),
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Exhibitor.objects.filter(event=self.event).exists())

    def test_signup_returns_404_for_unknown_event(self):
        self.client.force_login(self.user)

        response = _post(
            self.client,
            '/api/v2/exhibitor-signup/no-such-event/',
            _base_payload(),
        )

        self.assertEqual(response.status_code, 404)

    def test_signup_creates_new_exhibitor_and_org(self):
        self.client.force_login(self.user)

        response = _post(
            self.client,
            f'/api/v2/exhibitor-signup/{self.event.slug}/',
            _base_payload(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'status': 'created', 'message': 'Anmeldung erfolgreich erstellt.'},
        )
        self.assertTrue(Exhibitor.objects.filter(event=self.event).exists())
        org = Organisation.objects.get(org_name='Testverein')
        self.assertIn(self.user, org.members.all())

    def test_signup_with_attendances_and_assets(self):
        self.client.force_login(self.user)

        payload = _base_payload(
            attendances=[{'id': str(self.attendance.id), 'count': 2}],
            assets=[{'id': str(self.asset.id), 'count': 1}],
        )

        response = _post(
            self.client,
            f'/api/v2/exhibitor-signup/{self.event.slug}/',
            payload,
        )

        self.assertEqual(response.status_code, 200)
        exhibitor = Exhibitor.objects.get(event=self.event)
        self.assertEqual(exhibitor.attendances.count(), 1)
        self.assertEqual(exhibitor.assets.count(), 1)

    def test_signup_reuses_existing_organisation(self):
        self.client.force_login(self.user)
        existing_org = Organisation.objects.create(org_name='Existing Org')
        existing_org.members.add(self.user)

        response = _post(
            self.client,
            f'/api/v2/exhibitor-signup/{self.event.slug}/',
            _base_payload(org_id=str(existing_org.id)),
        )

        self.assertEqual(response.status_code, 200)
        exhibitor = Exhibitor.objects.get(event=self.event)
        self.assertEqual(exhibitor.organisation, existing_org)
        self.assertEqual(Organisation.objects.filter(org_name='Testverein').count(), 0)

    def test_signup_returns_exists_for_duplicate_submission(self):
        self.client.force_login(self.user)
        org = Organisation.objects.create(org_name='Dup Org')
        org.members.add(self.user)
        Exhibitor.objects.create(event=self.event, organisation=org)

        response = _post(
            self.client,
            f'/api/v2/exhibitor-signup/{self.event.slug}/',
            _base_payload(org_id=str(org.id)),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['status'], 'exists')

    @patch('rockon.api.endpoints.exhibitor_signup.send_mail_async')
    def test_signup_sends_admin_notification_when_group_has_members(
        self, send_mail_async
    ):
        admin_group = Group.objects.create(name='exhibitor_admins')
        admin_user = User.objects.create_user(
            username='exhibadmin',
            email='exhibadmin@example.com',
            password='secret',
        )
        admin_group.user_set.add(admin_user)

        self.client.force_login(self.user)

        response = _post(
            self.client,
            f'/api/v2/exhibitor-signup/{self.event.slug}/',
            _base_payload(),
        )

        self.assertEqual(response.status_code, 200)
        send_mail_async.assert_called_once()
        call_kwargs = send_mail_async.call_args.kwargs
        self.assertIn('exhibadmin@example.com', call_kwargs['recipient_list'])

    @patch('rockon.api.endpoints.exhibitor_signup.send_mail_async')
    def test_signup_does_not_fail_without_admin_group(self, send_mail_async):
        """Missing exhibitor_admins group is silently ignored."""
        self.client.force_login(self.user)

        response = _post(
            self.client,
            f'/api/v2/exhibitor-signup/{self.event.slug}/',
            _base_payload(),
        )

        self.assertEqual(response.status_code, 200)
        send_mail_async.assert_not_called()
