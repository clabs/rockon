from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from rockon.base.models import Event
from rockon.crew.models import CrewMember, GuestListEntry


@login_required
def mark_voucher(request):
    body = json.loads(request.body)

    if not body:
        return JsonResponse(
            {'status': 'error', 'message': 'No data provided'}, status=400
        )

    event = Event.objects.get(id=request.session.get('current_event_id'))

    crew_member = CrewMember.objects.get(user=request.user, crew__event=event)

    if not crew_member:
        return JsonResponse(
            {'status': 'error', 'message': 'User is not a crew member'}, status=400
        )

    try:
        voucher = crew_member.guestlist_entries.get(id=body.get('id'))
        voucher.send = not voucher.send
        voucher.save()
    except GuestListEntry.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Voucher not found'}, status=404
        )

    return JsonResponse(
        {'status': 'success', 'message': 'Voucher marked as sent'}, status=200
    )
