from __future__ import annotations

import json

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from django.utils.safestring import mark_safe

from rockon.base.models import Event, Organisation
from rockon.exhibitors.models import Asset, Attendance, Exhibitor


def join(request, slug):
    if not request.user.is_authenticated:
        url = reverse('base:login_request')
        url += '?ctx=exhibitors'
        return redirect(url)
    event = Event.objects.get(slug=slug)
    try:
        org = Organisation.objects.get(members__in=[request.user])
    except Organisation.DoesNotExist:
        org = None

    # Check if already submitted — show readonly view
    exhibitor = None
    readonly = False
    if org:
        try:
            exhibitor = Exhibitor.objects.get(organisation=org, event=event)
            readonly = True
        except Exhibitor.DoesNotExist:
            pass

    if not readonly and not request.user.profile.is_profile_complete_exhibitor():
        template = loader.get_template('exhibitor_join_profile_incomplete.html')
        extra_context = {
            'site_title': 'Profil unvollständig - Ausstelleranmeldung',
            'event': event,
            'slug': slug,
        }
        return HttpResponse(template.render(extra_context, request))

    template = loader.get_template('exhibitor_join.html')
    attendances = Attendance.objects.filter(event=event)
    assets = Asset.objects.all()

    # Serialize data as JSON for the Vue app
    attendances_json = mark_safe(
        json.dumps(
            [{'id': str(a.id), 'day': a.day.strftime('%d.%m.%Y')} for a in attendances]
        )
    )
    assets_json = mark_safe(
        json.dumps(
            [
                {
                    'id': str(a.id),
                    'name': a.name,
                    'description': a.description,
                    'is_bool': a.is_bool,
                }
                for a in assets
            ]
        )
    )
    org_json = mark_safe(
        json.dumps(
            {
                'id': str(org.id),
                'org_name': org.org_name,
                'org_address': org.org_address or '',
                'org_house_number': org.org_house_number or '',
                'org_address_extension': org.org_address_extension or '',
                'org_zip': org.org_zip or '',
                'org_place': org.org_place or '',
            }
            if org
            else None
        )
    )

    # Serialize submitted exhibitor data for readonly view
    exhibitor_json = mark_safe('null')
    if readonly and exhibitor:
        submitted_attendances = list(
            exhibitor.attendances.select_related('day').values_list('day__id', 'count')
        )
        submitted_assets = list(
            exhibitor.assets.select_related('asset').values_list('asset__id', 'count')
        )
        exhibitor_json = mark_safe(
            json.dumps(
                {
                    'offer_note': exhibitor.offer_note or '',
                    'general_note': exhibitor.general_note or '',
                    'website': exhibitor.website or '',
                    'logo_url': exhibitor.logo.url if exhibitor.logo else None,
                    'logo_name': exhibitor.logo.name.split('/')[-1]
                    if exhibitor.logo
                    else None,
                    'attendances': [
                        {'id': str(att_id), 'count': count}
                        for att_id, count in submitted_attendances
                    ],
                    'assets': [
                        {'id': str(asset_id), 'count': count}
                        for asset_id, count in submitted_assets
                    ],
                }
            )
        )

    extra_context = {
        'event': event,
        'site_title': 'Anmeldung' if not readonly else 'Anmeldung (eingereicht)',
        'attendances_json': attendances_json,
        'assets_json': assets_json,
        'org_json': org_json,
        'exhibitor_json': exhibitor_json,
        'readonly': readonly,
        'slug': slug,
        'org': org,
    }
    return HttpResponse(template.render(extra_context, request))
