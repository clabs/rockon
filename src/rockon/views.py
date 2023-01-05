from __future__ import annotations

from django.shortcuts import render


def error_404_view(request, exception):
    context = {"site_title": "Fehler 404"}
    return render(request, "errors/404.html", context)
