from __future__ import annotations

import os
import tempfile
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from rockon.base.models import Event
from rockon.crew.models import (
    Attendance,
    AttendancePhase,
    Crew,
    CrewMember,
    GuestListEntry,
)


class ImportVoucherCommandTests(TestCase):
    def setUp(self):
        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026')
        self.crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)
        self.attendance = Attendance.objects.create(
            event=self.event, day=self.event.start, phase=AttendancePhase.SHOW
        )
        self.member_one = self._create_member('member-one')
        self.member_two = self._create_member('member-two')

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

    def _create_member(self, username: str) -> CrewMember:
        user = User.objects.create_user(
            username=username, email=f'{username}@example.com', password='secret'
        )
        return CrewMember.objects.create(user=user, crew=self.crew)

    def _csv_path(self, rows: list[dict[str, str]]) -> str:
        fd, path = tempfile.mkstemp(suffix='.csv')
        self.addCleanup(os.remove, path)
        with os.fdopen(fd, 'w', newline='') as f:
            f.write('Voucher code,Product\n')
            for row in rows:
                f.write(f'{row["Voucher code"]},{row["Product"]}\n')
        return path

    def _call(self, rows, amount=2):
        call_command(
            'importvoucher',
            self._csv_path(rows),
            crew=str(self.crew.id),
            vouchertype='drink',
            eventday=str(self.attendance.id),
            amount=amount,
        )

    def test_assigns_requested_amount_to_each_crew_member(self):
        rows = [{'Voucher code': f'V{i}', 'Product': 'drink'} for i in range(1, 9)]
        self._call(rows, amount=2)

        self.assertEqual(
            GuestListEntry.objects.filter(crew_member=self.member_one).count(), 2
        )
        self.assertEqual(
            GuestListEntry.objects.filter(crew_member=self.member_two).count(), 2
        )

    def test_rows_with_other_vouchertype_are_ignored(self):
        rows = [
            {'Voucher code': 'FOOD-1', 'Product': 'food'},
            {'Voucher code': 'DRINK-1', 'Product': 'drink'},
            {'Voucher code': 'DRINK-2', 'Product': 'drink'},
        ]
        self._call(rows, amount=2)

        assigned = set(
            GuestListEntry.objects.filter(crew_member=self.member_one).values_list(
                'voucher', flat=True
            )
        )
        self.assertEqual(assigned, {'DRINK-1', 'DRINK-2'})

    def test_member_with_enough_vouchers_already_is_skipped(self):
        GuestListEntry.objects.create(
            crew_member=self.member_one, voucher='EXISTING-1', day=self.attendance
        )
        GuestListEntry.objects.create(
            crew_member=self.member_one, voucher='EXISTING-2', day=self.attendance
        )
        rows = [{'Voucher code': 'DRINK-1', 'Product': 'drink'}]

        self._call(rows, amount=2)

        self.assertEqual(
            GuestListEntry.objects.filter(crew_member=self.member_one).count(), 2
        )
        self.assertEqual(
            list(
                GuestListEntry.objects.filter(crew_member=self.member_two).values_list(
                    'voucher', flat=True
                )
            ),
            ['DRINK-1'],
        )

    def test_already_used_vouchers_are_excluded_from_pool(self):
        GuestListEntry.objects.create(
            crew_member=self.member_one, voucher='DRINK-1', day=self.attendance
        )
        rows = [
            {'Voucher code': 'DRINK-1', 'Product': 'drink'},
            {'Voucher code': 'DRINK-2', 'Product': 'drink'},
        ]

        self._call(rows, amount=1)

        # member_one already has DRINK-1 (>= amount), so gets skipped; the
        # only remaining pool entry (DRINK-2) goes to member_two.
        self.assertEqual(
            list(
                GuestListEntry.objects.filter(crew_member=self.member_two).values_list(
                    'voucher', flat=True
                )
            ),
            ['DRINK-2'],
        )

    def test_runs_out_of_vouchers_gracefully(self):
        rows = [{'Voucher code': 'DRINK-1', 'Product': 'drink'}]

        self._call(rows, amount=2)

        total_assigned = GuestListEntry.objects.count()
        self.assertEqual(total_assigned, 1)

    def test_unknown_eventday_raises_does_not_exist(self):
        with self.assertRaises(Attendance.DoesNotExist):
            call_command(
                'importvoucher',
                self._csv_path([]),
                crew=str(self.crew.id),
                vouchertype='drink',
                eventday='00000000-0000-0000-0000-000000000000',
                amount=2,
            )
