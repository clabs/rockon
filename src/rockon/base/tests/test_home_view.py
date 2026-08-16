from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.news.models import NewsPost, PostStatus


class HomeViewNewsFeedTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name='Rocktreff 2026',
            slug='rocktreff-2026',
            description='desc',
            start=date(2026, 7, 1),
            end=date(2026, 7, 3),
            setup_start=date(2026, 6, 29),
            setup_end=date(2026, 6, 30),
            opening=date(2026, 7, 1),
            closing=date(2026, 7, 2),
            teardown_start=date(2026, 7, 3),
            teardown_end=date(2026, 7, 4),
            location='Berlin',
            signup_type=SignUpType.CREW,
            signup_is_open=True,
            is_current=True,
        )
        self.crew_user = User.objects.create_user(
            username='crew-user', email='crew@example.com', password='secret'
        )
        self.crew_user.groups.add(Group.objects.create(name='crew'))
        self.exhibitor_user = User.objects.create_user(
            username='exhibitor-user', email='exhibitor@example.com', password='secret'
        )
        self.exhibitor_user.groups.add(Group.objects.create(name='exhibitors'))

    def test_feed_shows_matching_published_post_for_targeted_audience(self):
        NewsPost.objects.create(
            title='Crew news',
            body_markdown='hi crew',
            status=PostStatus.PUBLISHED,
            publish_at=timezone.now() - timedelta(hours=1),
            audience_crew=True,
        )
        self.client.force_login(self.crew_user)

        response = self.client.get(reverse('crm_user_home'))

        self.assertContains(response, 'Crew news')

    def test_feed_hides_post_from_non_targeted_audience(self):
        NewsPost.objects.create(
            title='Crew news',
            body_markdown='hi crew',
            status=PostStatus.PUBLISHED,
            publish_at=timezone.now() - timedelta(hours=1),
            audience_crew=True,
        )
        self.client.force_login(self.exhibitor_user)

        response = self.client.get(reverse('crm_user_home'))

        self.assertNotContains(response, 'Crew news')

    def test_feed_hides_draft_posts(self):
        NewsPost.objects.create(
            title='Draft news', body_markdown='hi', status=PostStatus.DRAFT
        )
        self.client.force_login(self.crew_user)

        response = self.client.get(reverse('crm_user_home'))

        self.assertNotContains(response, 'Draft news')

    def test_feed_hides_future_scheduled_posts(self):
        NewsPost.objects.create(
            title='Future news',
            body_markdown='hi',
            status=PostStatus.PUBLISHED,
            publish_at=timezone.now() + timedelta(hours=1),
        )
        self.client.force_login(self.crew_user)

        response = self.client.get(reverse('crm_user_home'))

        self.assertNotContains(response, 'Future news')
