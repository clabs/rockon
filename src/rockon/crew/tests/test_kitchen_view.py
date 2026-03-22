from __future__ import annotations

from datetime import date, time, timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.bands.models import Band, BandMember, Stage, TimeSlot
from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import (
    Attendance,
    AttendanceAddition,
    Crew,
    CrewMember,
    CrewMemberNutrion,
    CrewMemberStatus,
)


class KitchenAttendanceViewTests(TestCase):
    def setUp(self):
        self.catering_group = Group.objects.create(name='catering_food')
        self.catering_user = User.objects.create_user(
            username='catering-user',
            email='catering@example.com',
            password='secret',
        )
        self.catering_user.groups.add(self.catering_group)
        self.regular_user = User.objects.create_user(
            username='regular-user',
            email='regular@example.com',
            password='secret',
        )

        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026', 0)

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
        return reverse('crew:catering_attendance', kwargs={'slug': slug})

    def test_attendance_table_requires_login_and_group(self):
        response = self.client.get(self._url(self.event.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.regular_user)
        response = self.client.get(self._url(self.event.slug))
        self.assertEqual(response.status_code, 302)

    @patch('rockon.crew.views.kitchen.loader.get_template')
    def test_attendance_table_handles_unknown_event_slug(self, get_template):
        self.client.force_login(self.catering_user)
        get_template.return_value.render.return_value = ''

        response = self.client.get(self._url('missing'))

        self.assertEqual(response.status_code, 200)
        extra_context, request = get_template.return_value.render.call_args.args
        self.assertIsNone(extra_context['event'])
        self.assertEqual(extra_context['kitchen_list'], [])
        self.assertEqual(request.user, self.catering_user)

    @patch('rockon.crew.views.kitchen.loader.get_template')
    def test_attendance_table_builds_kitchen_list_with_crew_band_and_additions(
        self, get_template
    ):
        self.client.force_login(self.catering_user)
        get_template.return_value.render.return_value = ''

        crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)
        attendance = Attendance.objects.create(
            event=self.event,
            day=self.event.start,
            phase='show',
        )
        crew_user = User.objects.create_user(
            username='crew-member',
            email='member@example.com',
            password='secret',
            first_name='Crew',
            last_name='Member',
        )
        crew_member = CrewMember.objects.create(
            user=crew_user,
            crew=crew,
            state=CrewMemberStatus.CONFIRMED,
            nutrition=CrewMemberNutrion.OMNIVORE,
            nutrition_note='No peanuts',
            stays_overnight=True,
        )
        crew_member.attendance.add(attendance)
        AttendanceAddition.objects.create(
            attendance=attendance,
            amount=2,
            comment='Support team',
        )

        stage = Stage.objects.create(event=self.event, name='Main Stage')
        band = Band.objects.create(event=self.event, name='The Testers')
        band_member_user = User.objects.create_user(
            username='band-member',
            email='band-member@example.com',
            password='secret',
        )
        BandMember.objects.create(
            band=band,
            user=band_member_user,
            nutrition=CrewMemberNutrion.VEGAN,
        )
        TimeSlot.objects.create(
            stage=stage,
            day=attendance,
            start=time(18, 0),
            end=time(19, 0),
            band=band,
        )

        response = self.client.get(self._url(self.event.slug))

        self.assertEqual(response.status_code, 200)
        extra_context, _request = get_template.return_value.render.call_args.args
        self.assertEqual(extra_context['event'], self.event)
        self.assertEqual(len(extra_context['kitchen_list']), 1)
        day_amounts = extra_context['kitchen_list'][0]
        self.assertEqual(day_amounts['crew']['omnivore'], 1)
        self.assertEqual(day_amounts['bands']['vegan'], 1)
        self.assertEqual(day_amounts['misc'], 2)
        self.assertEqual(day_amounts['sum'], 4)
        self.assertEqual(len(extra_context['nutrition_notes']), 1)
        self.assertEqual(extra_context['nutrition_notes'][0]['note'], 'No peanuts')
        self.assertEqual(len(extra_context['addition_list']), 1)
        comments = [
            item['comment'] for item in extra_context['addition_list'][0]['additions']
        ]
        self.assertIn('Support team', comments)
        self.assertIn('The Testers', comments)
