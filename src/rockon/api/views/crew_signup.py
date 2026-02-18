from __future__ import annotations

import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.template import loader

from rockon.crew.models import Crew, CrewMember, Shirt, Team, TeamMember
from rockon.library.mailer import get_admin_url, send_mail_async

logger = logging.getLogger(__name__)


@login_required
def crew_signup(request, slug):
    # FIXME: refactor to Django forms to validate input
    body_list = json.loads(request.body)
    body = {}
    for item in body_list:
        body[item['name']] = item['value']

    _skills = [
        k.split('_')[1] for k, v in body.items() if k.startswith('skill_') and v == 'on'
    ]
    _attendance = [
        k.split('_')[1]
        for k, v in body.items()
        if k.startswith('attendance_') and v == 'on'
    ]

    _teamcategories = [
        k.split('_')[1]
        for k, v in body.items()
        if k.startswith('teamcategory_') and v == 'on'
    ]

    _teams = [
        k.split('_')[1] for k, v in body.items() if k.startswith('team_') and v == 'on'
    ]

    try:
        crew = Crew.objects.get(event__slug=slug)
    except Crew.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Crew not found'}, status=404
        )

    try:
        crew_member = CrewMember.objects.get(user=request.user, crew=crew)
    except CrewMember.DoesNotExist:
        crew_member = CrewMember.objects.create(
            user=request.user,
            crew=crew,
            shirt=Shirt.objects.get(id=body.get('crew_shirt')),
            nutrition=body.get('nutriton_type'),
            nutrition_note=body.get('nutrition_note'),
            skills_note=body.get('skills_note'),
            attendance_note=body.get('note_attendance'),
            stays_overnight=body.get('stays_overnight') == 'on',
            general_note=body.get('general_note'),
            needs_leave_of_absence=body.get('leave_of_absence') == 'on',
            leave_of_absence_note=body.get('leave_of_absence_note'),
        )

    crew_member.skills.add(*_skills)
    crew_member.attendance.add(*_attendance)
    crew_member.interested_in.add(*_teamcategories)
    TeamMember.objects.filter(
        crewmember=crew_member
    ).delete()  # remove all team memberships
    for team in _teams:
        team_id = Team.objects.get(id=team)
        TeamMember.objects.create(team=team_id, crewmember=crew_member)
    crew_member.save()

    _send_crewcoord_notification(crew, crew_member, _teams)

    return JsonResponse({'status': 'ok', 'message': 'signed up for crew successfully'})


def _send_crewcoord_notification(crew, crew_member, team_ids):
    """Notify crew coordinators about a new signup. Failures are logged, never block the response."""
    try:
        recipients = list(
            Group.objects.get(name='crewcoord').user_set.values_list('email', flat=True)
        )
        if not recipients:
            return

        user = crew_member.user
        team_names = (
            ', '.join(
                Team.objects.filter(id__in=team_ids).values_list('name', flat=True)
            )
            if team_ids
            else ''
        )

        admin_url = get_admin_url(crew_member)

        template = loader.get_template('mail/crew_signup.html')
        extra_context = {
            'event_name': crew.event.name,
            'member_name': f'{user.first_name} {user.last_name}',
            'teams': team_names,
            'admin_url': admin_url,
        }

        message = (
            f'Hallo Crew-Koordination,\nes gibt eine neue Crew-Anmeldung bei '
            f'{crew.event.name}.\nName: {extra_context["member_name"]}'
        )
        if team_names:
            message += f'\nGewünschte Teams: {team_names}'
        message += f'\n\nIm Admin ansehen: {admin_url}'

        send_mail_async(
            subject=f'{settings.EMAIL_SUBJECT_PREFIX} Neue Crew-Anmeldung',
            message=message,
            recipient_list=recipients,
            html_message=template.render(extra_context),
        )
    except Group.DoesNotExist:
        pass  # No crewcoord group configured
    except Exception:
        logger.exception('Error sending crew signup notification')
