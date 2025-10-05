from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from rockon.crew.models import Crew, CrewMember, Shirt, Team, TeamMember


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

    return JsonResponse({'status': 'ok', 'message': 'signed up for crew successfully'})
