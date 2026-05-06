from __future__ import annotations

import io
import math
import os
import tempfile
import zipfile
from datetime import datetime, timezone

import openpyxl
import openpyxl.utils
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth
from openpyxl.styles import Alignment, Font, PatternFill
from slugify import slugify

from rockon.base.models import Event
from rockon.exhibitors.models import Attendance, Exhibitor

exhibitorAdmin = Router()

_DE_WEEKDAYS = [
    'Montag',
    'Dienstag',
    'Mittwoch',
    'Donnerstag',
    'Freitag',
    'Samstag',
    'Sonntag',
]

_NOTE_COL_CHARS = 40  # approx chars per line at column width 40


def _estimate_lines(text: str | None, chars_per_line: int = _NOTE_COL_CHARS) -> int:
    if not text:
        return 1
    return sum(
        max(1, math.ceil(len(line) / chars_per_line)) for line in text.splitlines()
    )


@exhibitorAdmin.get(
    'export/{slug}/',
    url_name='exhibitor_export',
    auth=django_auth,
)
def exhibitor_export(request, slug: str):
    if not request.user.groups.filter(name='exhibitor_admins').exists():
        return HttpResponse(status=403)

    event = get_object_or_404(Event, slug=slug)

    days = list(Attendance.objects.filter(event=event).order_by('day'))

    exhibitors = list(
        Exhibitor.objects.filter(event=event)
        .select_related('organisation')
        .prefetch_related('attendances__day')
        .order_by('organisation__org_name')
    )

    now = datetime.now(tz=timezone.utc)
    ts = now.strftime('%Y%m%d-%H%M%S')

    org_width = min(
        60,
        max((len(ex.organisation.org_name) for ex in exhibitors), default=20) + 2,
    )
    logo_width = min(
        50,
        max(
            (len(os.path.basename(ex.logo.name)) for ex in exhibitors if ex.logo),
            default=20,
        )
        + 2,
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Aussteller'

    static_before = ['Markt-ID', 'Status', 'Organisation']
    day_headers = [_DE_WEEKDAYS[d.day.weekday()] for d in days]
    static_after = [
        'Website',
        'Allgemeine Anmerkung',
        'Über uns',
        'Angebot',
        'Logo-Dateiname',
    ]
    all_headers = static_before + day_headers + static_after

    ws.append(all_headers)

    header_fill = PatternFill(
        start_color='000000', end_color='000000', fill_type='solid'
    )
    header_font = Font(bold=True, color='FFFFFF')
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font

    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = f'A1:{openpyxl.utils.get_column_letter(len(all_headers))}1'

    widths = [12, 12, org_width] + [10] * len(days) + [28, 40, 40, 40, logo_width]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    # 1-based column indices for the three note fields
    note_col_indices = {5 + len(days), 6 + len(days), 7 + len(days)}

    alt_fill = PatternFill(start_color='FFF566', end_color='FFF566', fill_type='solid')
    wrap_top = Alignment(wrap_text=True, vertical='top')
    top = Alignment(vertical='top')

    for row_idx, ex in enumerate(exhibitors, 2):
        org = ex.organisation
        att_lookup = {ea.day_id: ea.count for ea in ex.attendances.all()}
        day_counts = ['✅' if att_lookup.get(d.id, 0) > 0 else '❌' for d in days]
        logo_filename = os.path.basename(ex.logo.name) if ex.logo else ''
        ws.append(
            [
                ex.market_id or '',
                ex.state,
                org.org_name,
                *day_counts,
                ex.website or '',
                ex.general_note or '',
                ex.about_note or '',
                ex.offer_note or '',
                logo_filename,
            ]
        )
        lines = max(
            _estimate_lines(ex.general_note),
            _estimate_lines(ex.about_note),
            _estimate_lines(ex.offer_note),
        )
        ws.row_dimensions[row_idx].height = min(max(20, lines * 16 + 8), 400)
        use_alt = row_idx % 2 == 1  # odd data rows get the tint
        for col_idx, cell in enumerate(ws[row_idx], 1):
            if use_alt:
                cell.fill = alt_fill
            cell.alignment = wrap_top if col_idx in note_col_indices else top

    ws.append([])
    ws.append(['Exportiert am', now.strftime('%d.%m.%Y %H:%M:%S UTC')])

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
            except FileNotFoundError, NotImplementedError:
                pass

    tmp.seek(0)
    return FileResponse(
        tmp,
        as_attachment=True,
        filename=f'exhibitors-{slug}-{ts}.zip',
        content_type='application/zip',
    )
