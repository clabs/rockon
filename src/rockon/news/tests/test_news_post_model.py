from __future__ import annotations

from django.db import IntegrityError, transaction
from django.test import TestCase

from rockon.news.models import NewsPost


class NewsPostModelTests(TestCase):
    def test_slug_is_auto_filled_from_title(self):
        post = NewsPost.objects.create(
            title='Hello World', body_markdown='hi', audience_crew=True
        )

        self.assertEqual(post.slug, 'hello-world')

    def test_slug_is_not_overwritten_when_set(self):
        post = NewsPost.objects.create(
            title='Hello World',
            slug='custom-slug',
            body_markdown='hi',
            audience_crew=True,
        )

        self.assertEqual(post.slug, 'custom-slug')

    def test_audience_must_be_explicit(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            NewsPost.objects.create(title='No audience', body_markdown='hi')

    def test_targets_audience_with_single_flag_matches_only_that_context(self):
        post = NewsPost.objects.create(
            title='Crew only', body_markdown='hi', audience_crew=True
        )

        self.assertTrue(post.targets_audience('crew'))
        self.assertFalse(post.targets_audience('bands'))
        self.assertFalse(post.targets_audience('exhibitors'))
        self.assertFalse(post.targets_audience(None))

    def test_targets_audience_with_all_flags_matches_every_context(self):
        post = NewsPost.objects.create(
            title='Everyone',
            body_markdown='hi',
            audience_crew=True,
            audience_bands=True,
            audience_exhibitors=True,
        )

        self.assertTrue(post.targets_audience('crew'))
        self.assertTrue(post.targets_audience('bands'))
        self.assertTrue(post.targets_audience('exhibitors'))
        self.assertFalse(post.targets_audience(None))
