from __future__ import annotations

from django.http import HttpResponse
from django.template import loader

from rockon.base.services import get_event_by_slug
from rockon.crew.models import Attendance, CrewMember, CrewMemberStatus
from rockon.library.decorators import require_group


@require_group('crewcoord')
def crew_availability_matrix(request, slug):
    template = loader.get_template('crewcoord_availability.html')
    event = get_event_by_slug(slug)

    attendance_days = []
    member_rows = []
    day_totals = []

    if event is not None:
        attendance_days = list(Attendance.objects.filter(event=event).order_by('day'))
        crew_members = list(
            CrewMember.objects.filter(
                crew__event=event,
                state=CrewMemberStatus.CONFIRMED,
            )
            .select_related('user', 'crew')
            .prefetch_related('attendance')
            .order_by('user__last_name', 'user__first_name')
        )

        member_availability_ids = {
            crew_member.id: {item.id for item in crew_member.attendance.all()}
            for crew_member in crew_members
        }

        day_totals = [
            {
                'attendance': attendance_day,
                'count': sum(
                    1
                    for crew_member in crew_members
                    if attendance_day.id in member_availability_ids[crew_member.id]
                ),
            }
            for attendance_day in attendance_days
        ]

        for crew_member in crew_members:
            available_day_ids = member_availability_ids[crew_member.id]
            member_rows.append(
                {
                    'member': crew_member,
                    'availability': [
                        {
                            'attendance': attendance_day,
                            'is_available': attendance_day.id in available_day_ids,
                        }
                        for attendance_day in attendance_days
                    ],
                    'available_count': sum(
                        1
                        for attendance_day in attendance_days
                        if attendance_day.id in available_day_ids
                    ),
                }
            )

    extra_context = {
        'event': event,
        'site_title': 'Verfügbarkeit',
        'attendance_days': attendance_days,
        'member_rows': member_rows,
        'day_totals': day_totals,
    }
    return HttpResponse(template.render(extra_context, request))
