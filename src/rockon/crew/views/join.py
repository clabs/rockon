from __future__ import annotations

from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.services import get_event_by_slug
from rockon.crew.models import Attendance, EventTeam, Shirt, Skill, Team, TeamCategory
from rockon.crew.models.attendance import AttendancePhase
from rockon.crew.models.crew_member import (
    CrewMember,
    CrewMemberNutrion,
    CrewMemberStatus,
)
from rockon.library.template_json import template_json


READONLY_CREW_STATES = {
    CrewMemberStatus.CONFIRMED,
}


def _build_initial_form_data(crew_member):
    if crew_member is None:
        return {
            'crew_shirt': '',
            'nutrition_type': '',
            'nutrition_note': '',
            'skills_note': '',
            'attendance_note': '',
            'stays_overnight': False,
            'general_note': '',
            'needs_leave_of_absence': False,
            'leave_of_absence_note': '',
            'skill_ids': [],
            'attendance_ids': [],
            'teamcategory_ids': [],
            'team_ids': [],
            'allow_contact': False,
            'read_privacy': False,
        }

    return {
        'crew_shirt': str(crew_member.shirt_id) if crew_member.shirt_id else '',
        'nutrition_type': (
            ''
            if crew_member.nutrition == CrewMemberNutrion.UNKNOWN
            else crew_member.nutrition
        ),
        'nutrition_note': crew_member.nutrition_note or '',
        'skills_note': crew_member.skills_note or '',
        'attendance_note': crew_member.attendance_note or '',
        'stays_overnight': bool(crew_member.stays_overnight),
        'general_note': crew_member.general_note or '',
        'needs_leave_of_absence': bool(crew_member.needs_leave_of_absence),
        'leave_of_absence_note': crew_member.leave_of_absence_note or '',
        'skill_ids': [
            str(skill_id)
            for skill_id in crew_member.skills.values_list('id', flat=True)
        ],
        'attendance_ids': [
            str(attendance_id)
            for attendance_id in crew_member.attendance.values_list('id', flat=True)
        ],
        'teamcategory_ids': [
            str(team_category_id)
            for team_category_id in crew_member.interested_in.values_list(
                'id', flat=True
            )
        ],
        'team_ids': [
            str(event_team_id)
            for event_team_id in crew_member.teams.values_list(
                'event_team_id', flat=True
            )
        ],
        'allow_contact': True,
        'read_privacy': True,
    }


def join(request, slug):
    if not request.user.is_authenticated:
        url = reverse('base:login_request')
        url += '?ctx=crew'
        return redirect(url)
    template = loader.get_template('join.html')
    event = get_event_by_slug(slug)
    if event is None:
        return HttpResponseNotFound()
    crew_member = (
        CrewMember.objects.filter(user=request.user, crew__event=event)
        .select_related('shirt')
        .prefetch_related('skills', 'attendance', 'interested_in', 'teams')
        .first()
    )
    crew_member_state = (
        crew_member.state if crew_member is not None else CrewMemberStatus.UNKNOWN
    )
    form_is_readonly = crew_member_state in READONLY_CREW_STATES
    initial_form_data = _build_initial_form_data(crew_member)

    if not request.user.profile.is_profile_complete_crew():
        template = loader.get_template('join_profile_incomplete.html')
        extra_context = {
            'site_title': 'Profil unvollständig - Crewanmeldung',
        }
        return HttpResponse(template.render(extra_context, request))

    shirts = Shirt.objects.all()
    skills = Skill.objects.all()
    attendance_days = Attendance.objects.filter(event=event)
    attendance_phases = []
    for phase_value, phase_name in AttendancePhase.choices:
        attendance_phases.append(
            {
                'phase': phase_value,
                'name': phase_name,
                'days': attendance_days.filter(phase=phase_value),
            }
        )
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

    shirts_json = template_json(
        [
            {
                'id': str(shirt.id),
                'name': str(shirt),
            }
            for shirt in shirts
        ],
        ensure_ascii=False,
    )
    skills_json = template_json(
        [
            {
                'id': str(skill.id),
                'name': skill.name,
                'explanation': skill.explanation,
                'icon': skill.icon,
            }
            for skill in skills
        ],
        ensure_ascii=False,
    )
    attendance_phases_json = template_json(
        [
            {
                'phase': phase['phase'],
                'name': phase['name'],
                'days': [
                    {
                        'id': str(day.id),
                        'label': str(day),
                    }
                    for day in phase['days']
                ],
            }
            for phase in attendance_phases
        ],
        ensure_ascii=False,
    )
    team_categories_json = template_json(
        [
            {
                'id': str(team_category.id),
                'name': team_category.name,
                'description': team_category.description,
                'image_url': team_category.get_image_url(),
                'teams': [
                    {
                        'id': str(team.join_event_links[0].id),
                        'name': team.name,
                    }
                    for team in getattr(team_category, 'teams').all()
                    if team.join_event_links
                ],
            }
            for team_category in team_categories
        ],
        ensure_ascii=False,
    )
    initial_form_data_json = template_json(initial_form_data, ensure_ascii=False)

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
        'shirts_json': shirts_json,
        'skills_json': skills_json,
        'attendance_phases_json': attendance_phases_json,
        'team_categories_json': team_categories_json,
        'initial_form_data_json': initial_form_data_json,
        'crew_member_state': crew_member_state,
        'form_is_readonly': form_is_readonly,
        'event_name': event.name,
        'event_image_url': event.get_image_url(),
    }
    return HttpResponse(template.render(extra_context, request))


def join_submitted(request, _slug):
    template = loader.get_template('join_submitted.html')
    extra_context = {'site_title': 'Anmeldung abgeschlossen'}
    return HttpResponse(template.render(extra_context, request))
