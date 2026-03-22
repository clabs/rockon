from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ExhibitorJoinViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='exhibitor-user',
            email='exhibitor@example.com',
            password='secret',
        )

    def test_join_view_returns_404_for_unknown_event_slug(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('exhibitors:join', kwargs={'slug': 'missing'})
        )

        self.assertEqual(response.status_code, 404)
