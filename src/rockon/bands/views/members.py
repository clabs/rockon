from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse
from django.template import loader

from rockon.bands.models import Band, BandMemberPosition
from rockon.crew.models import CrewMemberNutrion


@login_required
def members(request, slug, slug_guid):
    try:
        band_obj = Band.objects.get(slug=slug_guid)
    except (Band.DoesNotExist, ValidationError):
        raise Http404('Band nicht gefunden...')

    queryset = band_obj.band_members.all()
    count = queryset.count()

    members_values = list(queryset.values())
    user_ids = [m['user_id'] for m in members_values]
    users_by_id = {
        u.id: u for u in User.objects.filter(id__in=user_ids).select_related('profile')
    }
    for idx, member in enumerate(members_values):
        member['position_label'] = BandMemberPosition(member['position']).label
        member['nutrition_label'] = CrewMemberNutrion(member['nutrition']).label
        user = users_by_id.get(member['user_id'])
        member['user'] = (
            {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
            if user
            else {}
        )
        member['profile'] = model_to_dict(user.profile) if user else {}
        members_values[idx] = member

    rockon_data = {
        'band_id': str(band_obj.id),
        'api_signup': '/api/v2/bandmember-signup/',
        'max_members': 10,
        'current_members': members_values,
        'slots': 10 - count,
        'nutrition_choices': [
            {'value': c.value, 'label': c.label} for c in CrewMemberNutrion
        ],
        'position_choices': [
            {'value': c.value, 'label': c.label} for c in BandMemberPosition
        ],
    }

    template = loader.get_template('members.html')
    extra_context = {
        'site_title': 'Personenmeldung',
        'band': band_obj,
        'rockon_data_json': json.dumps(rockon_data, cls=DjangoJSONEncoder),
    }
    return HttpResponse(template.render(extra_context, request))
