from __future__ import annotations

from collections import defaultdict

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from rockon.base.models import Event
from rockon.crew.models import (
    Attendance,
    AttendanceAddition,
    Crew,
    CrewMember,
    CrewMemberStatus,
)
from rockon.exhibitors.models import Exhibitor, ExhibitorAttendance, ExhibitorStatus


@login_required
@user_passes_test(lambda u: u.groups.filter(name='catering_food').exists())
@cache_page(60 * 5)
@vary_on_cookie
def attendance_table(request, slug):
    template = loader.get_template('catering_attendance.html')
    event = Event.objects.filter(slug=slug).first()
    if not event:
        return HttpResponse(
            template.render({'event': None, 'kitchen_list': []}, request)
        )

    # timeslots with bands and their members
    attendances = Attendance.objects.filter(event=event).prefetch_related(
        'timeslots__band__band_members'
    )

    # crew members in a flat only id list
    crew_ids = Crew.objects.filter(event=event).values_list('id', flat=True)
    crew_members = CrewMember.objects.filter(crew_id__in=crew_ids).exclude(
        state__in=[CrewMemberStatus.UNKNOWN, CrewMemberStatus.REJECTED]
    )

    # nutrition notes with only required fields
    nutrion_notes = [
        {'crew_member': cm, 'note': cm.nutrition_note}
        for cm in crew_members.exclude(nutrition_note='')
        .exclude(nutrition_note__isnull=True)
        .select_related('user')
        .only('nutrition_note', 'user__first_name', 'user__last_name')
    ]

    # filter exhibitor attendance
    confirmed_exhibitor_ids = Exhibitor.objects.filter(
        event__in=event.sub_events.all(), state=ExhibitorStatus.CONFIRMED
    ).values_list('id', flat=True)

    # all attendance additions per day
    additions_by_day = defaultdict(lambda: {'sum': 0, 'items': []})
    for addition in AttendanceAddition.objects.filter(attendance__event=event).only(
        'attendance_id', 'amount', 'comment'
    ):
        additions_by_day[addition.attendance_id]['sum'] += addition.amount
        additions_by_day[addition.attendance_id]['items'].append(
            {'comment': addition.comment, 'amount': addition.amount}
        )

    # exhibitor attendance per day
    exhibitor_attendance_by_day = defaultdict(lambda: {'sum': 0, 'items': []})
    for ea in ExhibitorAttendance.objects.filter(
        exhibitor_id__in=confirmed_exhibitor_ids
    ).select_related('exhibitor__organisation', 'day'):
        exhibitor_attendance_by_day[ea.day.day]['sum'] += ea.count
        exhibitor_attendance_by_day[ea.day.day]['items'].append(
            {'comment': str(ea.exhibitor), 'amount': ea.count}
        )

    # aggregated query for all crew stats by attendance day
    crew_stats_by_day = {
        stat['attendance']: stat
        for stat in crew_members.filter(attendance__event=event)
        .values('attendance')
        .annotate(
            omnivore=Count('id', filter=Q(nutrition='omnivore')),
            vegetarian=Count('id', filter=Q(nutrition='vegetarian')),
            vegan=Count('id', filter=Q(nutrition='vegan')),
            total=Count('id'),
            omnivore_overnight=Count(
                'id', filter=Q(nutrition='omnivore', stays_overnight=True)
            ),
            vegetarian_overnight=Count(
                'id', filter=Q(nutrition='vegetarian', stays_overnight=True)
            ),
            vegan_overnight=Count(
                'id', filter=Q(nutrition='vegan', stays_overnight=True)
            ),
            total_overnight=Count('id', filter=Q(stays_overnight=True)),
        )
    }

    kitchen_list = []
    addtion_list = []
    previous_overnight = {}

    for day in attendances:
        stats = crew_stats_by_day.get(day.id, {})
        additions_data = additions_by_day[day.id]
        exhibitor_data = exhibitor_attendance_by_day[day.day]

        additions = additions_data['items'] + exhibitor_data['items']
        misc_total = additions_data['sum'] + exhibitor_data['sum']

        amounts = {
            'day': day,
            'misc': misc_total,
            'crew': {
                'omnivore': stats.get('omnivore', 0),
                'vegetarian': stats.get('vegetarian', 0),
                'vegan': stats.get('vegan', 0),
                'omnivore_overnight': stats.get('omnivore_overnight', 0),
                'vegetarian_overnight': stats.get('vegetarian_overnight', 0),
                'vegan_overnight': stats.get('vegan_overnight', 0),
                'sum_overnight': stats.get('total_overnight', 0),
                'omnivore_breakfast': previous_overnight.get('omnivore_overnight', 0),
                'vegetarian_breakfast': previous_overnight.get(
                    'vegetarian_overnight', 0
                ),
                'vegan_breakfast': previous_overnight.get('vegan_overnight', 0),
                'sum_breakfast': previous_overnight.get('total_overnight', 0),
            },
            'sum': stats.get('total', 0) + misc_total,
            'bands': {'omnivore': 0, 'vegetarian': 0, 'vegan': 0, 'sum': 0},
        }

        # band members need to eat too
        for timeslot in day.timeslots.all():
            if timeslot.band:
                band_members = timeslot.band.band_members.all()
                member_count = len(band_members)
                additions.append(
                    {'comment': timeslot.band.name, 'amount': member_count}
                )
                for member in band_members:
                    amounts['bands'][member.nutrition] += 1
                amounts['sum'] += member_count

        if additions:
            addtion_list.append({'day': day, 'additions': additions})

        previous_overnight = stats
        kitchen_list.append(amounts)

    extra_context = {
        'event': event,
        'kitchen_list': kitchen_list,
        'nutrion_notes': nutrion_notes,
        'addtion_list': addtion_list,
        'site_title': 'Mengenliste',
    }
    return HttpResponse(template.render(extra_context, request))
