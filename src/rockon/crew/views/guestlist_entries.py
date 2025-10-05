from __future__ import annotations


from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader

from rockon.base.models import Event
from rockon.crew.models import (
    CrewMember,
)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='crew').exists())
def guestlist_entries(request, slug) -> HttpResponse:
    template = loader.get_template('crew_guestlist_entries.html')
    event = Event.objects.get(slug=slug)
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
    guestlist_entries = crew_member.guestlist_entries.all().order_by('day')

    extra_context = {
        'event': event,
        'guestlist_entries': guestlist_entries,
        'site_title': 'Gästeliste',
    }
    return HttpResponse(template.render(extra_context, request))
