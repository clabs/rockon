from __future__ import annotations

import json

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse
from django.template import loader

from rockon.bands.models import Band, BandMemberPosition
from rockon.crew.models import CrewMemberNutrion


def members(request, slug, slug_guid):
    try:
        band_obj = Band.objects.get(slug=slug_guid)
    except Band.DoesNotExist, ValidationError:
        raise Http404('Band nicht gefunden...')

    members = band_obj.band_members.all()
    count = members.count()

    members_values = list(members.values())
    user_ids = [m['user_id'] for m in members_values]
    users_by_id = {
        u.id: u for u in User.objects.filter(id__in=user_ids).select_related('profile')
    }
    for idx, member in enumerate(members_values):
        member['position'] = BandMemberPosition(member['position']).label
        member['nutrition'] = CrewMemberNutrion(member['nutrition']).label
        user = users_by_id.get(member['user_id'])
        member['user'] = model_to_dict(user) if user else {}
        member['profile'] = model_to_dict(user.profile) if user else {}
        members_values[idx] = member

    template = loader.get_template('members.html')
    extra_context = {
        'site_title': 'Personenmeldung',
        'band': band_obj,
        'current_members': json.dumps(members_values, cls=DjangoJSONEncoder),
        'slots': 10 - count,
        'nutrion_choices': CrewMemberNutrion,
        'positions': BandMemberPosition,
    }
    return HttpResponse(template.render(extra_context, request))
