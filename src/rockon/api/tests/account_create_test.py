from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase


class AccountCreateApiTests(TestCase):
    def setUp(self):
        self.crew_group = Group.objects.create(name='crew')

    @patch('rockon.api.endpoints.account_create.EmailVerification.create_and_send')
    def test_create_account_assigns_valid_context_group(self, create_and_send):
        response = self.client.post(
            '/api/v2/account-create',
            data=json.dumps(
                {
                    'email': 'new-account@example.com',
                    'account_context': 'crew',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='new-account@example.com')
        self.assertTrue(user.groups.filter(id=self.crew_group.id).exists())
        create_and_send.assert_called_once_with(user=user)

    @patch('rockon.api.endpoints.account_create.EmailVerification.create_and_send')
    def test_create_account_ignores_invalid_context_group(self, create_and_send):
        response = self.client.post(
            '/api/v2/account-create',
            data=json.dumps(
                {
                    'email': 'invalid-context@example.com',
                    'account_context': 'invalid',
                }
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='invalid-context@example.com')
        self.assertFalse(user.groups.exists())
        create_and_send.assert_called_once_with(user=user)
