from __future__ import annotations

from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.models import Event
from rockon.crew.models import Attendance, EventTeam, Shirt, Skill, Team, TeamCategory
from rockon.crew.models.crew_member import CrewMember


def join(request, slug):
    if not request.user.is_authenticated:
        url = reverse('base:login_request')
        url += '?ctx=crew'
        return redirect(url)
    if CrewMember.objects.filter(user=request.user, crew__event__slug=slug).exists():
        return redirect('crew:join_submitted', slug=slug)
    template = loader.get_template('join.html')
    event = Event.objects.get(slug=slug)
    if not request.user.profile.is_profile_complete_crew():
        template = loader.get_template('join_profile_incomplete.html')
        extra_context = {
            'site_title': 'Profil unvollständig - Crewanmeldung',
        }
        return HttpResponse(template.render(extra_context, request))

    shirts = Shirt.objects.all()
    skills = Skill.objects.all()
    attendance_phases = Attendance.get_phases(event=event)
    join_event_teams = EventTeam.objects.filter(event=event).select_related('event')
    team_categories = (
        TeamCategory.objects.filter(
            teams__event_links__event=event,
            teams__is_public=True,
        )
        .distinct()
        .prefetch_related(
            Prefetch(
                'teams',
                queryset=Team.objects.filter(
                    event_links__event=event,
                    is_public=True,
                )
                .order_by('name')
                .prefetch_related(
                    Prefetch(
                        'event_links',
                        queryset=join_event_teams,
                        to_attr='join_event_links',
                    )
                ),
            )
        )
    )
    allow_overnight = request.user.profile.over_18()
    extra_context = {
        'og_title': f'Crewanmeldung {event.name}',
        'og_description': f'Crewanmeldung für die Veranstaltung {event.name}, sei Teil des Teams!',
        'shirts': shirts,
        'site_title': f'Crewanmeldung {event.name}',
        'skills': skills,
        'slug': slug,
        'team_categories': team_categories,
        'attendance_phases': attendance_phases,
        'allow_overnight': allow_overnight,
    }
    return HttpResponse(template.render(extra_context, request))


def join_submitted(request, slug):
    template = loader.get_template('join_submitted.html')
    extra_context = {'site_title': 'Anmeldung abgeschlossen'}
    return HttpResponse(template.render(extra_context, request))
