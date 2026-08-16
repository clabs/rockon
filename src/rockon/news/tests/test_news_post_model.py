from __future__ import annotations

from django.test import TestCase

from rockon.news.models import NewsPost


class NewsPostModelTests(TestCase):
    def test_slug_is_auto_filled_from_title(self):
        post = NewsPost.objects.create(title='Hello World', body_markdown='hi')

        self.assertEqual(post.slug, 'hello-world')

    def test_slug_is_not_overwritten_when_set(self):
        post = NewsPost.objects.create(
            title='Hello World', slug='custom-slug', body_markdown='hi'
        )

        self.assertEqual(post.slug, 'custom-slug')

    def test_targets_audience_with_no_flags_matches_any_context(self):
        post = NewsPost.objects.create(title='For everyone', body_markdown='hi')

        self.assertTrue(post.targets_audience('crew'))
        self.assertTrue(post.targets_audience('bands'))
        self.assertTrue(post.targets_audience('exhibitors'))
        self.assertTrue(post.targets_audience(None))

    def test_targets_audience_with_single_flag_matches_only_that_context(self):
        post = NewsPost.objects.create(
            title='Crew only', body_markdown='hi', audience_crew=True
        )

        self.assertTrue(post.targets_audience('crew'))
        self.assertFalse(post.targets_audience('bands'))
        self.assertFalse(post.targets_audience('exhibitors'))
        self.assertFalse(post.targets_audience(None))
