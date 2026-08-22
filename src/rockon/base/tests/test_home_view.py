from __future__ import annotations

from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import Crew, CrewDate, CrewDateResponse, CrewMember
from rockon.news.models import NewsPost, PostStatus


def _make_event(slug: str = 'rocktreff-2026', *, is_current: bool = True) -> Event:
    start = date(2026, 7, 1)
    return Event.objects.create(
        name='Rocktreff 2026',
        slug=slug,
        description='desc',
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
        is_current=is_current,
    )


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='home-user',
            email='home@example.com',
            password='secret',
            first_name='Home',
            last_name='User',
        )
        self.event = _make_event()
        self.crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)

    def test_redirects_anonymous_user(self):
        response = self.client.get(reverse('crm_user_home'))

        self.assertEqual(response.status_code, 302)

    def test_no_sidebar_for_non_crew_member(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('crm_user_home'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'crew-dates-sidebar')

    def test_no_sidebar_for_unconfirmed_crew_member(self):
        CrewMember.objects.create(user=self.user, crew=self.crew, state='unknown')
        self.client.force_login(self.user)

        response = self.client.get(reverse('crm_user_home'))

        self.assertNotContains(response, 'crew-dates-sidebar')

    def test_sidebar_shows_upcoming_dates_with_current_status(self):
        CrewMember.objects.create(user=self.user, crew=self.crew, state='confirmed')
        today = timezone.localdate()

        upcoming = CrewDate.objects.create(
            crew=self.crew,
            title='Aufbau-Meeting',
            description='Besprechung zum Aufbau',
            date=today + timedelta(days=5),
            start_time=time(18, 0),
            end_time=time(19, 0),
        )
        past = CrewDate.objects.create(
            crew=self.crew,
            title='Vergangenes Treffen',
            date=today - timedelta(days=5),
            start_time=time(18, 0),
            end_time=time(19, 0),
        )
        CrewDateResponse.objects.create(
            crew_date=upcoming, user=self.user, status='tentative'
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('crm_user_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'crew-dates-sidebar')
        self.assertContains(response, 'Aufbau-Meeting')
        self.assertNotContains(response, 'Vergangenes Treffen')
        self.assertContains(response, 'data-status="tentative"')
        self.assertContains(response, f'data-crew-date-id="{upcoming.id}"')
        self.assertNotContains(response, str(past.id))


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
            title='Draft news',
            body_markdown='hi',
            status=PostStatus.DRAFT,
            audience_crew=True,
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
            audience_crew=True,
        )
        self.client.force_login(self.crew_user)

        response = self.client.get(reverse('crm_user_home'))

        self.assertNotContains(response, 'Future news')
