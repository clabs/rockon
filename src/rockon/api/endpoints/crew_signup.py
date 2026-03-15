from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import transaction
from django.template import loader
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.crew_signup import CrewSignupIn
from rockon.api.schemas.status import StatusOut
from rockon.crew.models import (
    Crew,
    CrewMember,
    EventTeam,
    Shirt,
    TeamCategory,
    TeamMember,
)
from rockon.library.mailer import get_admin_url, send_mail_async

logger = logging.getLogger(__name__)

crewSignupRouter = Router()


@crewSignupRouter.post(
    '/{slug}/',
    response={200: StatusOut, 400: StatusOut, 404: StatusOut},
    url_name='crew_signup',
    auth=django_auth,
)
def crew_signup(request, slug: str, data: CrewSignupIn):
    """Sign up the authenticated user for a crew."""
    try:
        crew = Crew.objects.get(event__slug=slug)
    except Crew.DoesNotExist:
        return 404, {'status': 'error', 'message': 'Crew not found'}

    with transaction.atomic():
        try:
            crew_member = CrewMember.objects.get(user=request.user, crew=crew)
            shirt = Shirt.objects.get(id=data.crew_shirt)

            crew_member.shirt = shirt
            crew_member.nutrition = data.nutrition_type
            crew_member.nutrition_note = data.nutrition_note
            crew_member.skills_note = data.skills_note
            crew_member.attendance_note = data.attendance_note
            crew_member.stays_overnight = data.stays_overnight
            crew_member.general_note = data.general_note
            crew_member.needs_leave_of_absence = data.needs_leave_of_absence
            crew_member.leave_of_absence_note = data.leave_of_absence_note
        except CrewMember.DoesNotExist:
            shirt = Shirt.objects.get(id=data.crew_shirt)
            crew_member = CrewMember.objects.create(
                user=request.user,
                crew=crew,
                shirt=shirt,
                nutrition=data.nutrition_type,
                nutrition_note=data.nutrition_note,
                skills_note=data.skills_note,
                attendance_note=data.attendance_note,
                stays_overnight=data.stays_overnight,
                general_note=data.general_note,
                needs_leave_of_absence=data.needs_leave_of_absence,
                leave_of_absence_note=data.leave_of_absence_note,
            )

        event_teams = EventTeam.objects.filter(
            event=crew.event, id__in=data.team_ids
        ).select_related('team')
        if event_teams.count() != len(set(data.team_ids)):
            return 400, {
                'status': 'error',
                'message': 'Invalid team selection for event',
            }

        allowed_teamcategory_ids = set(
            TeamCategory.objects.filter(teams__event_links__event=crew.event)
            .distinct()
            .values_list('id', flat=True)
        )
        selected_teamcategory_ids = set(data.teamcategory_ids)
        if not selected_teamcategory_ids.issubset(allowed_teamcategory_ids):
            return 400, {
                'status': 'error',
                'message': 'Invalid team category selection for event',
            }

        crew_member.save()
        crew_member.skills.set(data.skill_ids)
        crew_member.attendance.set(data.attendance_ids)
        crew_member.interested_in.set(selected_teamcategory_ids)
        TeamMember.objects.filter(
            crewmember=crew_member
        ).delete()  # remove all team memberships
        for event_team in event_teams:
            TeamMember.objects.create(event_team=event_team, crewmember=crew_member)

    _send_crewcoord_notification(crew, crew_member, event_teams)

    return 200, {'status': 'ok', 'message': 'signed up for crew successfully'}


def _send_crewcoord_notification(crew, crew_member, event_teams):
    """Notify crew coordinators about a new signup. Failures are logged, never block the response."""
    try:
        recipients = list(
            Group.objects.get(name='crewcoord').user_set.values_list('email', flat=True)
        )
        if not recipients:
            return

        user = crew_member.user
        team_names = (
            ', '.join(event_teams.values_list('team__name', flat=True))
            if event_teams
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
