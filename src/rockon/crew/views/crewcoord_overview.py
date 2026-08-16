from __future__ import annotations

from django.db.models import Count
from django.http import HttpResponse
from django.template import loader

from rockon.base.services import get_event_by_slug
from rockon.crew.models import Attendance, Crew, CrewMember, CrewMemberStatus, Shirt
from rockon.library.decorators import require_group


@require_group('crewcoord')
def crew_chart(request, slug):
    template = loader.get_template('crew_overview.html')
    event = get_event_by_slug(slug)
    attendances = []
    attendances_unknown = []
    if event is not None:
        attendances = (
            Attendance.objects.filter(
                event=event,
                crew_members__state=CrewMemberStatus.CONFIRMED,
            )
            .order_by('day')
            .annotate(no_of_crew_members=Count('crew_members'))
        )
        attendances_unknown = (
            Attendance.objects.filter(
                event=event,
                crew_members__state__in=[
                    CrewMemberStatus.UNKNOWN,
                    CrewMemberStatus.REJECTED,
                ],
            )
            .order_by('day')
            .annotate(no_of_crew_members=Count('crew_members'))
        )

    extra_context = {
        'event': event,
        'site_title': 'Übersicht',
        'attendances_unknown': attendances_unknown,
        'attendances': attendances,
    }
    return HttpResponse(template.render(extra_context, request))


@require_group('crewcoord')
def crew_shirts(request, slug):
    template = loader.get_template('crewcoord_tshirts.html')
    event = get_event_by_slug(slug)
    counts = []
    crew_members = []
    if event is not None:
        crews = Crew.objects.filter(event=event)
        crew_members = CrewMember.objects.filter(crew__in=crews).exclude(
            state__in=[CrewMemberStatus.UNKNOWN, CrewMemberStatus.REJECTED]
        )

        shirts = Shirt.objects.all()

        shirt_counts_qs = crew_members.values('shirt').annotate(
            shirt_count=Count('shirt'),
        )
        shirt_count_map = {
            item['shirt']: item['shirt_count'] for item in shirt_counts_qs
        }
        counts = [
            {'shirt': shirt, 'count': shirt_count_map.get(shirt.id, 0)}
            for shirt in shirts
        ]

    extra_context = {
        'event': event,
        'site_title': 'T-Shirts',
        'counts': counts,
        'sum': sum(count['count'] for count in counts),
        'crew_members': crew_members,
    }
    return HttpResponse(template.render(extra_context, request))
