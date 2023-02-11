# from __future__ import annotations

from __future__ import annotations

from django.shortcuts import render


def custom_bad_request_view(request, exception=None):
    context = {"site_title": "Fehler 400", "reason": exception}
    return render(request, "errors/400.html", context, status=400)


def custom_permission_denied_view(request, exception=None):
    context = {"site_title": "Fehler 403", "reason": exception}
    return render(request, "errors/403.html", context, status=403)


def custom_page_not_found_view(request, exception):
    context = {"site_title": "Fehler 404", "reason": exception}
    return render(request, "errors/404.html", context, status=404)


def custom_error_view(request, exception=None):
    context = {"site_title": "Fehler 500", "reason": exception}
    return render(request, "errors/500.html", context, status=500)
