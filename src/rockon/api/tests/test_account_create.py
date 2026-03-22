from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase


class AccountCreateApiTests(TestCase):
    def setUp(self):
        self.crew_group = Group.objects.create(name='crew')

    def _post(self, *, email: str, account_context: str = 'crew'):
        return self.client.post(
            '/api/v2/account-create',
            data=json.dumps(
                {
                    'email': email,
                    'account_context': account_context,
                }
            ),
            content_type='application/json',
        )

    @patch('rockon.api.endpoints.account_create.EmailVerification.create_and_send')
    def test_create_account_assigns_valid_context_group(self, create_and_send):
        response = self._post(email='new-account@example.com')

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='new-account@example.com')
        self.assertTrue(user.groups.filter(id=self.crew_group.id).exists())
        create_and_send.assert_called_once_with(user=user)

    @patch('rockon.api.endpoints.account_create.EmailVerification.create_and_send')
    def test_create_account_ignores_invalid_context_group(self, create_and_send):
        response = self._post(
            email='invalid-context@example.com',
            account_context='invalid',
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='invalid-context@example.com')
        self.assertFalse(user.groups.exists())
        create_and_send.assert_called_once_with(user=user)

    @patch('rockon.api.endpoints.account_create.EmailVerification.create_and_send')
    def test_create_account_normalizes_email_before_saving(self, create_and_send):
        response = self._post(email='  New-Account@Example.com  ')

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='new-account@example.com')
        self.assertEqual(user.username, 'new-account@example.com')
        create_and_send.assert_called_once_with(user=user)

    @patch('rockon.api.endpoints.account_create.EmailVerification.create_and_send')
    def test_create_account_rejects_existing_user_case_insensitive(
        self, create_and_send
    ):
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password=None,
        )

        response = self._post(email='  Existing@Example.com  ')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {'status': 'exists', 'message': 'User already exists'},
        )
        create_and_send.assert_not_called()

    @patch('rockon.api.endpoints.account_create.EmailVerification.create_and_send')
    def test_create_account_requires_non_blank_email(self, create_and_send):
        response = self._post(email='   ')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {'status': 'error', 'message': 'Email is required'},
        )
        create_and_send.assert_not_called()

    @patch('rockon.api.endpoints.account_create.EmailVerification.create_and_send')
    def test_create_account_ignores_missing_group_for_supported_context(
        self, create_and_send
    ):
        response = self._post(
            email='exhibitor@example.com',
            account_context='exhibitors',
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='exhibitor@example.com')
        self.assertFalse(user.groups.exists())
        create_and_send.assert_called_once_with(user=user)

    @patch(
        'rockon.api.endpoints.account_create.EmailVerification.create_and_send',
        side_effect=RuntimeError('mail failed'),
    )
    def test_create_account_rolls_back_user_when_verification_fails(
        self, create_and_send
    ):
        with self.assertRaises(RuntimeError):
            self._post(email='rollback@example.com')

        self.assertFalse(User.objects.filter(email='rollback@example.com').exists())
        create_and_send.assert_called_once()
