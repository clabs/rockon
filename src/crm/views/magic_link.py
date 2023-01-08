from __future__ import annotations

from django.http import Http404, HttpResponse, JsonResponse
from django.template import loader

from crm.models import MagicLink, Person


def request_magic_link(request):
    template = loader.get_template("crm/magic_link.html")
    context = {
        "site_title": "Magic Link",
    }
    return HttpResponse(template.render(context, request))


def request_magic_link_submitted(request):
    template = loader.get_template("crm/magic_link_requested.html")
    context = {
        "site_title": "Magic Link angefordert",
    }
    return HttpResponse(template.render(context, request))


def magic_link(request, token):
    """Shows information corresponding to the magic link token."""
    try:
        magic_link = MagicLink.objects.get(token=token)
        person = Person.objects.get(id=magic_link.person.id)
        # FIXME: this should be a redirect to a page that shows the information
        return JsonResponse(
            {"status": "success", "message": "Magic link found", "person": str(person)}
        )
    except (MagicLink.DoesNotExist, Person.DoesNotExist):
        raise Http404("Der angefrate Schlüssel wurde nicht gefunden...")
