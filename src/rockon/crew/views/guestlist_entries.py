from __future__ import annotations

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.template import loader

from rockon.base.services import get_event_by_slug
from rockon.crew.models import (
    CrewMember,
)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='crew').exists())
def guestlist_entries(request, slug) -> HttpResponse:
    template = loader.get_template('crew_guestlist_entries.html')
    event = get_event_by_slug(slug)
    if event is None:
        return HttpResponseNotFound()
    try:
        crew_member = CrewMember.objects.get(user=request.user, crew__event=event)
    except CrewMember.DoesNotExist:
        template = loader.get_template('errors/403.html')
        return HttpResponseForbidden(
            template.render(
                {'more_info': 'Du bist kein Mitglied der Crews dieser Veranstaltung.'},
                request,
            )
        )
    vouchers = crew_member.guestlist_entries.select_related('day').order_by('day')

    extra_context = {
        'event': event,
        'guestlist_entries': vouchers,
        'site_title': 'Gästeliste',
    }
    return HttpResponse(template.render(extra_context, request))
