from __future__ import annotations

from django.shortcuts import get_object_or_404, redirect

from rockon.base.models import Event


def check_band_application_open(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        slug = kwargs.get("slug", None)
        if not slug:
            slug = Event.objects.filter(is_current=True).first().slug
        event = get_object_or_404(Event, slug=slug)
        if not event.band_application_open:
            return redirect("bands:bid_closed", slug=slug)
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func
