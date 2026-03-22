from __future__ import annotations

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class AccountContextAssignmentViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='account-user',
            email='account@example.com',
            password='secret',
        )
        self.crew_group = Group.objects.create(name='crew')

    def test_account_view_assigns_valid_context_group(self):
        self.client.force_login(self.user)

        with patch('rockon.base.views.account.loader.get_template') as get_template:
            get_template.return_value.render.return_value = ''
            response = self.client.get(f'{reverse("base:account")}?ctx=crew')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.groups.filter(id=self.crew_group.id).exists())

    def test_account_view_ignores_invalid_context_group(self):
        self.client.force_login(self.user)

        with patch('rockon.base.views.account.loader.get_template') as get_template:
            get_template.return_value.render.return_value = ''
            response = self.client.get(f'{reverse("base:account")}?ctx=invalid')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.groups.exists())
