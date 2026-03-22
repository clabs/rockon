from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.base.services.account_context import assign_account_context_group


class AssignAccountContextGroupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='context-user',
            email='context@example.com',
            password='secret',
        )
        self.crew_group = Group.objects.create(name='crew')

    def test_assign_account_context_group_adds_existing_supported_group(self):
        assigned = assign_account_context_group(self.user, 'crew')

        self.assertTrue(assigned)
        self.assertTrue(self.user.groups.filter(id=self.crew_group.id).exists())

    def test_assign_account_context_group_rejects_unsupported_context(self):
        assigned = assign_account_context_group(self.user, 'invalid')

        self.assertFalse(assigned)
        self.assertFalse(self.user.groups.exists())

    def test_assign_account_context_group_returns_false_for_missing_group(self):
        assigned = assign_account_context_group(self.user, 'bands')

        self.assertFalse(assigned)
        self.assertFalse(self.user.groups.exists())


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

    def test_account_view_ignores_supported_context_when_group_is_missing(self):
        self.client.force_login(self.user)

        with patch('rockon.base.views.account.loader.get_template') as get_template:
            get_template.return_value.render.return_value = ''
            response = self.client.get(f'{reverse("base:account")}?ctx=bands')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.groups.exists())
