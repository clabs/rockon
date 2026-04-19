from __future__ import annotations

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template import loader

from rockon.base.services import get_event_by_slug
from rockon.exhibitors.models import Asset, Attendance, Exhibitor


@login_required
@user_passes_test(lambda u: u.groups.filter(name='exhibitor_admins').exists())
def exhibitor_assets(request, slug):
    template = loader.get_template('exhibitor_assets.html')
    event = get_event_by_slug(slug)

    if event is None:
        return HttpResponse(status=404)

    days = list(Attendance.objects.filter(event=event))
    assets = list(Asset.objects.all())

    exhibitors = (
        Exhibitor.objects.filter(event=event)
        .select_related('organisation')
        .prefetch_related('attendances__day', 'assets__asset')
        .order_by('organisation__org_name')
    )

    rows = []
    day_totals = [0] * len(days)
    asset_totals = [0] * len(assets)
    overall_total = 0
    for exhibitor in exhibitors:
        attendance_by_day = {ea.day_id: ea.count for ea in exhibitor.attendances.all()}
        asset_by_id = {ea.asset_id: ea.count for ea in exhibitor.assets.all()}

        day_cells = []
        attendance_total = 0
        for day in days:
            count = attendance_by_day.get(day.id)
            selected = count is not None
            day_cells.append({'selected': selected})
            if selected:
                attendance_total += 1
                day_totals[len(day_cells) - 1] += 1

        asset_cells = []
        for asset in assets:
            count = asset_by_id.get(asset.id)
            asset_cells.append(
                {
                    'count': count,
                    'selected': count is not None,
                    'is_bool': asset.is_bool,
                }
            )
            if count is not None:
                asset_totals[len(asset_cells) - 1] += 1 if asset.is_bool else count

        rows.append(
            {
                'exhibitor': exhibitor,
                'day_cells': day_cells,
                'asset_cells': asset_cells,
                'attendance_total': attendance_total,
            }
        )
        overall_total += attendance_total

    extra_context = {
        'site_title': 'Aussteller Infrastruktur',
        'rows': rows,
        'days': days,
        'assets': assets,
        'day_totals': day_totals,
        'asset_totals': asset_totals,
        'overall_total': overall_total,
        'event': event,
        'event_slug': slug,
    }
    return HttpResponse(template.render(extra_context, request))
