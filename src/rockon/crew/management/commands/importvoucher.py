from __future__ import annotations

import argparse
import csv
import uuid

from django.core.management.base import BaseCommand, CommandError

from rockon.crew.models.attendance import Attendance
from rockon.crew.models.crew_member import CrewMember
from rockon.crew.models.guestlist_entry import GuestListEntry


class Command(BaseCommand):
    help = "Imports vouchers from a CSV file with specified vouchertype and eventday"

    def add_arguments(self, parser):
        parser.add_argument("--crew", type=uuid.UUID, help="Crew UUID", required=True)
        parser.add_argument(
            "--vouchertype", type=str, help="Type of the voucher", required=True
        )
        parser.add_argument(
            "--eventday", type=uuid.UUID, help="Event day UUID", required=True
        )
        parser.add_argument(
            "--amount", type=int, help="Amount of vouchers to import", default=2
        )
        parser.add_argument(
            "file",
            type=argparse.FileType("r"),
            help="Path to the CSV file containing vouchers",
        )

    def handle(self, *args, **options):
        crew = options["crew"]
        vouchertype = options["vouchertype"]
        eventday = options["eventday"]
        amount = options["amount"]
        file = options["file"]

        print(f"Crew: {crew}")
        print(f"Voucher type: {vouchertype}")
        print(f"Event day: {eventday}")
        print(f"File: {file.name}")

        vouchers_list = []
        reader = csv.DictReader(file)
        for row in reader:
            vouchers_list.append(row)

        eventday = Attendance.objects.get(pk=eventday)

        print(f"Event day: {eventday}")

        used_vouchers = GuestListEntry.objects.filter(day=eventday).values_list(
            "voucher", flat=True
        )

        available_vouchers = [
            voucher
            for voucher in vouchers_list
            if voucher["Voucher code"] not in used_vouchers
            and voucher["Product"] == vouchertype
        ]

        crew_members = CrewMember.objects.filter(crew=crew)

        for crew_member in crew_members:
            has_voucher = GuestListEntry.objects.filter(
                crew_member=crew_member, day=eventday
            ).count()
            if has_voucher >= amount:
                print(
                    f'Crew member "{crew_member}" already has specified amount of vouchers'
                )
                continue
            voucher_codes = [
                voucher["Voucher code"] for voucher in available_vouchers[:amount]
            ]
            available_vouchers = available_vouchers[amount:]
            print(f'Assigning voucher "{voucher_codes}" to crew member "{crew_member}"')
            for voucher_code in voucher_codes:
                GuestListEntry.objects.create(
                    crew_member=crew_member, voucher=voucher_code, day=eventday
                )

        print(f"Available vouchers: {len(available_vouchers)}")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported vouchers for type "{vouchertype}" and event day "{eventday}"'
            )
        )
