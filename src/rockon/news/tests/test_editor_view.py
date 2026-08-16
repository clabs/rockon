from __future__ import annotations

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.news.models import NewsPost


class EditorViewTests(TestCase):
    def setUp(self):
        self.editors_group = Group.objects.create(name='news_editors')
        self.editor = User.objects.create_user(
            username='editor', email='editor@example.com', password='secret'
        )
        self.editor.groups.add(self.editors_group)

        self.regular_user = User.objects.create_user(
            username='regular', email='regular@example.com', password='secret'
        )

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(reverse('news:editor'))

        self.assertEqual(response.status_code, 302)

    def test_non_editor_is_redirected(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(reverse('news:editor'))

        self.assertEqual(response.status_code, 302)

    def test_editor_can_access_and_sees_posts(self):
        NewsPost.objects.create(title='Hi', body_markdown='hi', audience_crew=True)
        self.client.force_login(self.editor)

        response = self.client.get(reverse('news:editor'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hi')
