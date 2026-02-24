from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.template import loader
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.crew_signup import CrewSignupIn
from rockon.api.schemas.status import StatusOut
from rockon.crew.models import Crew, CrewMember, Shirt, Team, TeamMember
from rockon.library.mailer import get_admin_url, send_mail_async

logger = logging.getLogger(__name__)

crewSignupRouter = Router()


@crewSignupRouter.post(
    '/{slug}/',
    response={200: StatusOut, 404: StatusOut},
    url_name='crew_signup',
    auth=django_auth,
)
def crew_signup(request, slug: str, data: CrewSignupIn):
    """Sign up the authenticated user for a crew."""
    try:
        crew = Crew.objects.get(event__slug=slug)
    except Crew.DoesNotExist:
        return 404, {'status': 'error', 'message': 'Crew not found'}

    try:
        crew_member = CrewMember.objects.get(user=request.user, crew=crew)
    except CrewMember.DoesNotExist:
        crew_member = CrewMember.objects.create(
            user=request.user,
            crew=crew,
            shirt=Shirt.objects.get(id=data.crew_shirt),
            nutrition=data.nutrition_type,
            nutrition_note=data.nutrition_note,
            skills_note=data.skills_note,
            attendance_note=data.attendance_note,
            stays_overnight=data.stays_overnight,
            general_note=data.general_note,
            needs_leave_of_absence=data.needs_leave_of_absence,
            leave_of_absence_note=data.leave_of_absence_note,
        )

    crew_member.skills.add(*data.skill_ids)
    crew_member.attendance.add(*data.attendance_ids)
    crew_member.interested_in.add(*data.teamcategory_ids)
    TeamMember.objects.filter(
        crewmember=crew_member
    ).delete()  # remove all team memberships
    for team_id in data.team_ids:
        team = Team.objects.get(id=team_id)
        TeamMember.objects.create(team=team, crewmember=crew_member)
    crew_member.save()

    _send_crewcoord_notification(crew, crew_member, data.team_ids)

    return 200, {'status': 'ok', 'message': 'signed up for crew successfully'}


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
