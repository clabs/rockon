from __future__ import annotations

import io
import os
import tempfile
import zipfile
from datetime import datetime, timezone

import openpyxl
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth
from slugify import slugify

from rockon.base.models import Event
from rockon.exhibitors.models import Exhibitor

exhibitorAdmin = Router()

_XLSX_HEADERS = [
    'Markt-ID',
    'Status',
    'Organisation',
    'Adresse',
    'Adresszusatz',
    'PLZ',
    'Ort',
    'Website',
    'Allgemeine Anmerkung',
    'Über uns',
    'Angebot',
    'Logo-Dateiname',
    'Anwesenheit',
    'Ausstattung',
]


@exhibitorAdmin.get(
    'export/{slug}/',
    url_name='exhibitor_export',
    auth=django_auth,
)
def exhibitor_export(request, slug: str):
    if not request.user.groups.filter(name='exhibitor_admins').exists():
        return HttpResponse(status=403)

    event = get_object_or_404(Event, slug=slug)

    exhibitors = (
        Exhibitor.objects.filter(event=event)
        .select_related('organisation')
        .prefetch_related('attendances__day', 'assets__asset')
        .order_by('organisation__org_name')
    )

    now = datetime.now(tz=timezone.utc)
    ts = now.strftime('%Y%m%d-%H%M%S')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Aussteller'
    ws.append(['Exportiert am', now.strftime('%d.%m.%Y %H:%M:%S UTC')])
    ws.append([])
    ws.append(_XLSX_HEADERS)

    for ex in exhibitors:
        org = ex.organisation
        address = ' '.join(filter(None, [org.org_address, org.org_house_number]))
        attendances = ';'.join(
            f'{a.day.day}:{a.count}' for a in ex.attendances.all()
        )
        assets = ';'.join(
            f'{a.asset.name}:{a.count}' for a in ex.assets.all()
        )
        logo_filename = os.path.basename(ex.logo.name) if ex.logo else ''
        ws.append([
            ex.market_id or '',
            ex.state,
            org.org_name,
            address,
            org.org_address_extension or '',
            org.org_zip or '',
            org.org_place or '',
            ex.website or '',
            ex.general_note or '',
            ex.about_note or '',
            ex.offer_note or '',
            logo_filename,
            attendances,
            assets,
        ])

    xlsx_buf = io.BytesIO()
    wb.save(xlsx_buf)

    tmp = tempfile.TemporaryFile()
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('exhibitors.xlsx', xlsx_buf.getvalue())
        zf.writestr(f'export-{ts}.txt', '')
        for ex in exhibitors:
            if not ex.logo:
                continue
            try:
                logo_path = ex.logo.path
                org_slug = slugify(ex.organisation.org_name)
                arcname = f'logos/{org_slug}-{os.path.basename(ex.logo.name)}'
                zf.write(logo_path, arcname)
            except (FileNotFoundError, NotImplementedError):
                pass

    tmp.seek(0)
    return FileResponse(
        tmp,
        as_attachment=True,
        filename=f'exhibitors-{slug}-{ts}.zip',
        content_type='application/zip',
    )
