from __future__ import annotations

import json
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

from django.contrib.auth.models import User
from django.test import TestCase

from rockon.base.models import EmailVerification, Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import Attendance, Crew, CrewMember, GuestListEntry


class MiscApiEndpointsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='api-user',
            email='api-user@example.com',
            password='secret',
            first_name='Api',
            last_name='User',
        )
        self.client.force_login(self.user)

        self.event = self._create_event(
            name='Rocktreff 2026',
            slug='rocktreff-2026',
            offset_days=0,
        )
        self.crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)
        self.crew_member = CrewMember.objects.create(user=self.user, crew=self.crew)
        self.attendance = Attendance.objects.create(
            event=self.event,
            day=self.event.start,
            phase='show',
        )

    def _create_event(self, *, name: str, slug: str, offset_days: int) -> Event:
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

    def test_user_email_update_rejects_mismatch(self):
        response = self.client.post(
            '/api/v2/user-email/',
            data=json.dumps(
                {
                    'changeEmailNew': 'new@example.com',
                    'changeEmailRepeat': 'other@example.com',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'status': 'error', 'message': 'E-Mail is required'},
        )

    @patch('rockon.api.endpoints.user_email.EmailVerification.create_and_send')
    def test_user_email_update_deletes_previous_tokens_and_sends_new_one(
        self, create_and_send
    ):
        EmailVerification.objects.create(user=self.user)

        response = self.client.post(
            '/api/v2/user-email/',
            data=json.dumps(
                {
                    'changeEmailNew': 'New@Example.COM',
                    'changeEmailRepeat': 'New@Example.COM',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'status': 'ok', 'message': 'E-Mail updated'},
        )
        self.assertFalse(EmailVerification.objects.filter(user=self.user).exists())
        create_and_send.assert_called_once_with(
            user=self.user, new_email='new@example.com'
        )

    def test_user_profile_update_persists_names_and_profile_fields(self):
        response = self.client.post(
            '/api/v2/user-profile/',
            data=json.dumps(
                {
                    'first_name': 'Renamed',
                    'last_name': 'User',
                    'nick_name': 'Rockstar',
                    'phone': '030123456',
                    'address': 'Teststrasse',
                    'address_extension': '2. OG',
                    'address_housenumber': '42',
                    'zip_code': '10999',
                    'place': 'Berlin',
                    'user_birthday': '1990-01-01',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'status': 'ok', 'message': 'Profile updated'},
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Renamed')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.profile.nick_name, 'Rockstar')
        self.assertEqual(self.user.profile.phone, '030123456')
        self.assertEqual(self.user.profile.birthday.isoformat(), '1990-01-01')

    def test_verify_email_returns_error_for_unknown_token(self):
        response = self.client.post(
            '/api/v2/verify-email/',
            data=json.dumps({'token': 'not-a-token'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': ''})

    def test_verify_email_marks_profile_verified_and_consumes_token(self):
        verification = EmailVerification.objects.create(user=self.user)
        self.user.profile.email_is_verified = False
        self.user.profile.save(update_fields=['email_is_verified'])

        response = self.client.post(
            '/api/v2/verify-email/',
            data=json.dumps({'token': str(verification.token)}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'status': 'verified', 'next': '/account/'},
        )
        self.user.refresh_from_db()
        verification.refresh_from_db()
        self.assertTrue(self.user.profile.email_is_verified)
        self.assertFalse(verification.is_active)

    def test_verify_email_reports_spent_token(self):
        verification = EmailVerification.objects.create(user=self.user, is_active=False)

        response = self.client.post(
            '/api/v2/verify-email/',
            data=json.dumps({'token': str(verification.token)}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, {'status': 'token_spent', 'next': ''})

    def test_mark_voucher_toggles_send_flag(self):
        voucher = GuestListEntry.objects.create(
            crew_member=self.crew_member,
            voucher='voucher-1',
            day=self.attendance,
            send=False,
        )

        response = self.client.post(
            '/api/v2/mark-voucher',
            data=json.dumps({'id': str(voucher.id)}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 204)
        voucher.refresh_from_db()
        self.assertTrue(voucher.send)

    def test_mark_voucher_returns_404_for_foreign_voucher(self):
        other_user = User.objects.create_user(
            username='other-user',
            email='other@example.com',
            password='secret',
        )
        other_member = CrewMember.objects.create(user=other_user, crew=self.crew)
        voucher = GuestListEntry.objects.create(
            crew_member=other_member,
            voucher='voucher-2',
            day=self.attendance,
            send=False,
        )

        response = self.client.post(
            '/api/v2/mark-voucher',
            data=json.dumps({'id': str(voucher.id)}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)

    @patch(
        'rockon.api.endpoints.request_magic_link.MagicLink.acreate_and_send',
        new_callable=AsyncMock,
    )
    def test_request_magic_link_sends_for_active_user(self, acreate_and_send):
        response = self.client.post(
            '/api/v2/request-magic-link',
            data=json.dumps({'email': ' API-USER@example.com '}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'status': 'ok', 'message': 'Magic link sent if mail matches a user.'},
        )
        acreate_and_send.assert_awaited_once_with(self.user)

    @patch(
        'rockon.api.endpoints.request_magic_link.MagicLink.acreate_and_send',
        new_callable=AsyncMock,
    )
    def test_request_magic_link_returns_404_for_unknown_user(self, acreate_and_send):
        response = self.client.post(
            '/api/v2/request-magic-link',
            data=json.dumps({'email': 'missing@example.com'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)
        acreate_and_send.assert_not_awaited()
