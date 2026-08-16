from __future__ import annotations

from datetime import date as date_cls
from datetime import time as time_cls

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from rockon.base.services import get_event_by_slug
from rockon.crew.models import Crew, CrewDate
from rockon.library.decorators import require_group


def _parse_date_fields(request):
    """Parse and validate the date/time fields shared by create and update.

    Returns (fields, error_message). fields is None when validation fails.
    """
    title = (request.POST.get('title') or '').strip()
    description = (request.POST.get('description') or '').strip()
    date_raw = request.POST.get('date') or ''
    start_time_raw = request.POST.get('start_time') or ''
    end_time_raw = request.POST.get('end_time') or ''

    if not title:
        return None, 'Titel wird benötigt.'

    try:
        date_value = date_cls.fromisoformat(date_raw)
        start_time = time_cls.fromisoformat(start_time_raw)
        end_time = time_cls.fromisoformat(end_time_raw)
    except ValueError:
        return None, 'Ungültiges Datum oder ungültige Uhrzeit.'

    if end_time <= start_time:
        return None, 'Die Endzeit muss nach der Startzeit liegen.'

    return {
        'title': title,
        'description': description,
        'date': date_value,
        'start_time': start_time,
        'end_time': end_time,
    }, None


@require_group('crewcoord')
def crew_dates_management(request, slug):
    template = loader.get_template('crewcoord_dates.html')
    event = get_event_by_slug(slug)
    crew = Crew.objects.filter(event=event).first() if event is not None else None

    if request.method == 'POST' and event is not None:
        action = request.POST.get('action')

        if crew is None:
            messages.error(request, 'Keine Crew für dieses Event konfiguriert.')
        elif action == 'create':
            fields, error = _parse_date_fields(request)
            if error:
                messages.error(request, error)
            else:
                CrewDate.objects.create(crew=crew, **fields)
                messages.success(request, 'Termin wurde angelegt.')
        elif action == 'update':
            crew_date = CrewDate.objects.filter(
                id=request.POST.get('crew_date_id'), crew=crew
            ).first()
            if crew_date is None:
                messages.error(request, 'Ungültiger Termin für dieses Event.')
            else:
                fields, error = _parse_date_fields(request)
                if error:
                    messages.error(request, error)
                else:
                    for field, value in fields.items():
                        setattr(crew_date, field, value)
                    crew_date.save(update_fields=[*fields.keys(), 'updated_at'])
                    messages.success(request, 'Termin wurde aktualisiert.')
        elif action == 'delete':
            deleted, _ = CrewDate.objects.filter(
                id=request.POST.get('crew_date_id'), crew=crew
            ).delete()
            if deleted:
                messages.success(request, 'Termin wurde gelöscht.')
            else:
                messages.error(request, 'Ungültiger Termin für dieses Event.')
        else:
            messages.error(request, 'Unbekannte Aktion.')

        return redirect('crew:coord_dates', slug=slug)

    dates = list(CrewDate.objects.filter(crew=crew)) if crew is not None else []

    extra_context = {
        'event': event,
        'site_title': 'Termine',
        'dates': dates,
        'has_crew': crew is not None,
    }
    return HttpResponse(template.render(extra_context, request))
