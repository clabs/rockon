from __future__ import annotations

from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import Crew, CrewDate


class CrewCoordDatesManagementTests(TestCase):
    def setUp(self):
        self.crewcoord_group = Group.objects.create(name='crewcoord')

        self.crewcoord_user = User.objects.create_user(
            username='coord',
            email='coord@example.com',
            password='secret',
            first_name='Coord',
            last_name='User',
        )
        self.crewcoord_user.groups.add(self.crewcoord_group)

        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='secret',
            first_name='Regular',
            last_name='User',
        )

        self.event_one = self._create_event('Rocktreff 2026', 'rocktreff-2026', 0)
        self.event_two = self._create_event('Rocktreff 2027', 'rocktreff-2027', 400)

        self.crew_one = Crew.objects.create(
            event=self.event_one, name='Crew 2026', year=2026
        )
        self.crew_two = Crew.objects.create(
            event=self.event_two, name='Crew 2027', year=2027
        )

        self.crew_date = CrewDate.objects.create(
            crew=self.crew_one,
            title='Aufbau-Meeting',
            description='Besprechung zum Aufbau',
            date=date(2026, 6, 20),
            start_time=time(18, 0),
            end_time=time(19, 0),
        )
        self.crew_date_other_event = CrewDate.objects.create(
            crew=self.crew_two,
            title='Anderes Meeting',
            description='',
            date=date(2027, 6, 20),
            start_time=time(18, 0),
            end_time=time(19, 0),
        )

    def _create_event(self, name: str, slug: str, offset_days: int) -> Event:
        start = date(2026, 7, 1) + timedelta(days=offset_days)
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

    def _url(self, slug: str) -> str:
        return reverse('crew:coord_dates', kwargs={'slug': slug})

    def test_access_control(self):
        response = self.client.get(self._url(self.event_one.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.regular_user)
        response = self.client.get(self._url(self.event_one.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.crewcoord_user)
        response = self.client.get(self._url(self.event_one.slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aufbau-Meeting')
        self.assertNotContains(response, 'Anderes Meeting')

    def test_view_handles_unknown_event_slug(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.get(self._url('unknown-event'))
        self.assertEqual(response.status_code, 200)

    def test_create_date(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'create',
                'title': 'Workshop-Tag',
                'description': 'Löten lernen',
                'date': '2026-06-25',
                'start_time': '10:00',
                'end_time': '16:00',
            },
        )
        self.assertRedirects(response, self._url(self.event_one.slug))

        created = CrewDate.objects.get(title='Workshop-Tag')
        self.assertEqual(created.crew, self.crew_one)
        self.assertEqual(created.date, date(2026, 6, 25))
        self.assertEqual(created.start_time, time(10, 0))
        self.assertEqual(created.end_time, time(16, 0))

    def test_create_date_rejects_end_before_start(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'create',
                'title': 'Ungueltig',
                'description': '',
                'date': '2026-06-25',
                'start_time': '16:00',
                'end_time': '10:00',
            },
            follow=True,
        )
        self.assertContains(response, 'Endzeit muss nach der Startzeit liegen')
        self.assertFalse(CrewDate.objects.filter(title='Ungueltig').exists())

    def test_update_date(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'update',
                'crew_date_id': str(self.crew_date.id),
                'title': 'Aufbau-Meeting (verschoben)',
                'description': self.crew_date.description,
                'date': '2026-06-21',
                'start_time': '19:00',
                'end_time': '20:00',
            },
        )
        self.assertRedirects(response, self._url(self.event_one.slug))

        self.crew_date.refresh_from_db()
        self.assertEqual(self.crew_date.title, 'Aufbau-Meeting (verschoben)')
        self.assertEqual(self.crew_date.date, date(2026, 6, 21))

    def test_update_date_rejects_cross_event_id(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'update',
                'crew_date_id': str(self.crew_date_other_event.id),
                'title': 'Uebernommen',
                'description': '',
                'date': '2026-06-21',
                'start_time': '19:00',
                'end_time': '20:00',
            },
            follow=True,
        )
        self.assertContains(response, 'Ungültiger Termin für dieses Event.')

        self.crew_date_other_event.refresh_from_db()
        self.assertEqual(self.crew_date_other_event.title, 'Anderes Meeting')

    def test_delete_date(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._url(self.event_one.slug),
            {'action': 'delete', 'crew_date_id': str(self.crew_date.id)},
        )
        self.assertRedirects(response, self._url(self.event_one.slug))
        self.assertFalse(CrewDate.objects.filter(id=self.crew_date.id).exists())

    def test_unknown_action(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._url(self.event_one.slug),
            {'action': 'nonsense'},
            follow=True,
        )
        self.assertContains(response, 'Unbekannte Aktion.')
