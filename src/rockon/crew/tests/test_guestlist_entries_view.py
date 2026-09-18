from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event
from rockon.crew.models import (
    Attendance,
    AttendancePhase,
    Crew,
    CrewMember,
    GuestListEntry,
)


class GuestlistEntriesViewTests(TestCase):
    def setUp(self):
        self.crew_group = Group.objects.create(name='crew')
        self.member_user = User.objects.create_user(
            username='crew-member', email='member@example.com', password='secret'
        )
        self.member_user.groups.add(self.crew_group)
        self.non_member_user = User.objects.create_user(
            username='non-member', email='non-member@example.com', password='secret'
        )
        self.non_member_user.groups.add(self.crew_group)

        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026')
        self.crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)

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
        )

    def _url(self, slug: str) -> str:
        return reverse('crew:guestlist_entries', kwargs={'slug': slug})

    def test_requires_login(self):
        response = self.client.get(self._url(self.event.slug))
        self.assertEqual(response.status_code, 302)

    def test_unknown_event_slug_returns_404(self):
        self.client.force_login(self.member_user)
        response = self.client.get(self._url('missing'))
        self.assertEqual(response.status_code, 404)

    @patch('rockon.crew.views.guestlist_entries.loader.get_template')
    def test_non_crew_member_gets_403(self, get_template):
        get_template.return_value.render.return_value = ''
        self.client.force_login(self.non_member_user)

        response = self.client.get(self._url(self.event.slug))

        self.assertEqual(response.status_code, 403)
        get_template.assert_called_with('errors/403.html')

    @patch('rockon.crew.views.guestlist_entries.loader.get_template')
    def test_crew_member_sees_only_own_vouchers(self, get_template):
        get_template.return_value.render.return_value = ''
        self.client.force_login(self.member_user)

        member = CrewMember.objects.create(user=self.member_user, crew=self.crew)
        other_user = User.objects.create_user(
            username='other-crew', email='other@example.com', password='secret'
        )
        other_member = CrewMember.objects.create(user=other_user, crew=self.crew)

        attendance = Attendance.objects.create(
            event=self.event, day=self.event.start, phase=AttendancePhase.SHOW
        )
        own_entry = GuestListEntry.objects.create(
            crew_member=member, voucher='VOUCHER-1', day=attendance
        )
        GuestListEntry.objects.create(
            crew_member=other_member, voucher='VOUCHER-2', day=attendance
        )

        response = self.client.get(self._url(self.event.slug))

        self.assertEqual(response.status_code, 200)
        extra_context, _request = get_template.return_value.render.call_args.args
        vouchers = list(extra_context['guestlist_entries'])
        self.assertEqual(vouchers, [own_entry])
