"""rockon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import TemplateView

admin.site.site_header = "rockon backstage"
admin.site.site_title = "backstage | rockon"

urlpatterns = [
    path("", include("rockon.urls_homepage")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("backstage/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/bb-legacy/", include("bblegacy.urls")),
    path("bands/", include("bands.urls")),
    path("crew/", include("crew.urls")),
    path("crm/", include("crm.urls")),
    path("exhibitors/", include("exhibitors.urls")),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
    path("to/", include("tools.urls_shortener")),
    path("tools/", include("tools.urls")),
    path("uploads/bids/<str:bid_id>/<str:media_id>", include("bblegacy.urls_media")),
]

handler404 = "rockon.views.custom_page_not_found_view"
handler500 = "rockon.views.custom_error_view"
handler403 = "rockon.views.custom_permission_denied_view"
handler400 = "rockon.views.custom_bad_request_view"

# enable debug toolbar if DEBUG is True
if settings.DEBUG:
    debug_overlay = path("__debug__/", include("debug_toolbar.urls"))
    urlpatterns.append(debug_overlay)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
