from __future__ import annotations

import json
from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.utils import timezone

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.news.models import NewsPost, PostStatus


class NewsEndpointTests(TestCase):
    def setUp(self):
        self.editors_group = Group.objects.create(name='news_editors')
        self.editor = User.objects.create_user(
            username='editor', email='editor@example.com', password='secret'
        )
        self.editor.groups.add(self.editors_group)

        self.regular_user = User.objects.create_user(
            username='regular', email='regular@example.com', password='secret'
        )

        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026')

    def _create_event(self, name: str, slug: str) -> Event:
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
            signup_type=SignUpType.CREW,
            signup_is_open=True,
        )

    def test_list_requires_news_editor_group(self):
        self.client.force_login(self.regular_user)

        response = self.client.get('/api/v2/news/')

        self.assertEqual(response.status_code, 403)

    def test_create_requires_news_editor_group(self):
        self.client.force_login(self.regular_user)

        response = self.client.post(
            '/api/v2/news/',
            data=json.dumps({'title': 'Hi', 'body_markdown': 'hi'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_create_renders_and_sanitizes_markdown(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            '/api/v2/news/',
            data=json.dumps(
                {'title': 'Hi', 'body_markdown': '# Hi\n\n<script>alert(1)</script>'}
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIn('<h1>Hi</h1>', payload['body_html'])
        self.assertNotIn('<script>', payload['body_html'])
        self.assertEqual(payload['status'], 'draft')
        self.assertIsNone(payload['publish_at'])

    def test_publishing_without_publish_at_sets_it_to_now(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            '/api/v2/news/',
            data=json.dumps(
                {'title': 'Hi', 'body_markdown': 'hi', 'status': 'published'}
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIsNotNone(payload['publish_at'])

    def test_patch_updates_rendered_html(self):
        self.client.force_login(self.editor)
        post = NewsPost.objects.create(title='Hi', body_markdown='old')

        response = self.client.patch(
            f'/api/v2/news/{post.id}/',
            data=json.dumps({'body_markdown': 'new **content**'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('<strong>content</strong>', payload['body_html'])

    def test_patch_requires_news_editor_group(self):
        self.client.force_login(self.regular_user)
        post = NewsPost.objects.create(title='Hi', body_markdown='old')

        response = self.client.patch(
            f'/api/v2/news/{post.id}/',
            data=json.dumps({'title': 'New'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_removes_post(self):
        self.client.force_login(self.editor)
        post = NewsPost.objects.create(title='Hi', body_markdown='old')

        response = self.client.delete(f'/api/v2/news/{post.id}/')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(NewsPost.objects.filter(id=post.id).exists())

    def test_delete_requires_news_editor_group(self):
        self.client.force_login(self.regular_user)
        post = NewsPost.objects.create(title='Hi', body_markdown='old')

        response = self.client.delete(f'/api/v2/news/{post.id}/')

        self.assertEqual(response.status_code, 403)
        self.assertTrue(NewsPost.objects.filter(id=post.id).exists())

    def test_preview_sanitizes_and_persists_nothing(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            '/api/v2/news/preview/',
            data=json.dumps({'body_markdown': '<script>alert(1)</script>text'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<script>', response.json()['body_html'])
        self.assertFalse(NewsPost.objects.exists())

    def test_preview_requires_news_editor_group(self):
        self.client.force_login(self.regular_user)

        response = self.client.post(
            '/api/v2/news/preview/',
            data=json.dumps({'body_markdown': 'hi'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_list_filters_by_event_and_status(self):
        self.client.force_login(self.editor)
        NewsPost.objects.create(
            title='Draft', body_markdown='x', event=self.event, status=PostStatus.DRAFT
        )
        NewsPost.objects.create(
            title='Published',
            body_markdown='x',
            event=self.event,
            status=PostStatus.PUBLISHED,
            publish_at=timezone.now(),
        )

        response = self.client.get(
            f'/api/v2/news/?event={self.event.slug}&status=published'
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['title'], 'Published')
