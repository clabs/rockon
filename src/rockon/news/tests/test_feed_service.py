from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.news.models import NewsPost, PostStatus
from rockon.news.services.feed import visible_posts_for_user


class VisiblePostsForUserTests(TestCase):
    def setUp(self):
        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026')
        self.other_event = self._create_event('Rocktreff 2027', 'rocktreff-2027')
        self.now = timezone.now()

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

    def _create_post(self, **kwargs) -> NewsPost:
        defaults = {
            'title': 'Post',
            'body_markdown': 'body',
            'status': PostStatus.PUBLISHED,
            'publish_at': self.now - timedelta(hours=1),
        }
        defaults.update(kwargs)
        return NewsPost.objects.create(**defaults)

    def test_draft_posts_are_excluded(self):
        self._create_post(status=PostStatus.DRAFT)

        self.assertEqual(visible_posts_for_user(None, self.event, 'crew'), [])

    def test_future_publish_at_is_excluded(self):
        self._create_post(publish_at=self.now + timedelta(hours=1))

        self.assertEqual(visible_posts_for_user(None, self.event, 'crew'), [])

    def test_null_publish_at_is_excluded(self):
        self._create_post(publish_at=None)

        self.assertEqual(visible_posts_for_user(None, self.event, 'crew'), [])

    def test_mismatched_event_is_excluded(self):
        self._create_post(event=self.other_event)

        self.assertEqual(visible_posts_for_user(None, self.event, 'crew'), [])

    def test_global_post_is_included_regardless_of_event(self):
        post = self._create_post(event=None)

        self.assertEqual(visible_posts_for_user(None, self.event, 'crew'), [post])

    def test_matching_event_is_included(self):
        post = self._create_post(event=self.event)

        self.assertEqual(visible_posts_for_user(None, self.event, 'crew'), [post])

    def test_audience_filtering_per_context(self):
        post = self._create_post(audience_crew=True)

        self.assertEqual(visible_posts_for_user(None, self.event, 'crew'), [post])
        self.assertEqual(visible_posts_for_user(None, self.event, 'exhibitors'), [])
        self.assertEqual(visible_posts_for_user(None, self.event, None), [])

    def test_empty_audience_is_visible_to_every_context(self):
        post = self._create_post()

        self.assertEqual(visible_posts_for_user(None, self.event, 'crew'), [post])
        self.assertEqual(visible_posts_for_user(None, self.event, 'exhibitors'), [post])
        self.assertEqual(visible_posts_for_user(None, self.event, None), [post])
