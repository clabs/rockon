from __future__ import annotations

from datetime import date, timedelta

from django.http import Http404, HttpResponse
from django.test import RequestFactory, TestCase
from django.utils import timezone

from rockon.base.models import Event
from rockon.library.decorators import check_band_application_open


@check_band_application_open
def _dummy_view(request, slug):
    return HttpResponse('ok')


class CheckBandApplicationOpenTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _create_event(self, slug: str, **overrides) -> Event:
        start = date(2026, 7, 1)
        defaults = {
            'name': 'Rocktreff 2026',
            'slug': slug,
            'description': 'desc',
            'start': start,
            'end': start + timedelta(days=2),
            'setup_start': start - timedelta(days=2),
            'setup_end': start - timedelta(days=1),
            'opening': start,
            'closing': start + timedelta(days=1),
            'teardown_start': start + timedelta(days=2),
            'teardown_end': start + timedelta(days=3),
            'location': 'Berlin',
        }
        defaults.update(overrides)
        return Event.objects.create(**defaults)

    def test_unknown_slug_raises_404(self):
        request = self.factory.get('/')
        with self.assertRaises(Http404):
            _dummy_view(request, slug='missing')

    def test_application_open_passes_through_to_view(self):
        now = timezone.now()
        self._create_event(
            'open-event',
            band_application_start=now - timedelta(days=1),
            band_application_end=now + timedelta(days=1),
        )
        request = self.factory.get('/')

        response = _dummy_view(request, slug='open-event')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')

    def test_application_closed_redirects_to_bid_closed(self):
        now = timezone.now()
        self._create_event(
            'closed-event',
            band_application_start=now - timedelta(days=10),
            band_application_end=now - timedelta(days=1),
        )
        request = self.factory.get('/')

        response = _dummy_view(request, slug='closed-event')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/closed-event/bands/bid/closed/', response.url)
