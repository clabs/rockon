from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from rockon.base.models import Event
from rockon.base.models.event import SignUpType


class EventModelTests(TestCase):
    def _create_event(
        self,
        name: str,
        *,
        start_offset_days: int = 0,
        **overrides,
    ) -> Event:
        start = date(2026, 7, 1) + timedelta(days=start_offset_days)
        defaults = {
            'slug': overrides.pop('slug', name.lower().replace(' ', '-')),
            'description': f'{name} description',
            'start': start,
            'end': start + timedelta(days=2),
            'setup_start': start - timedelta(days=2),
            'setup_end': start - timedelta(days=1),
            'opening': start,
            'closing': start + timedelta(days=1),
            'teardown_start': start + timedelta(days=2),
            'teardown_end': start + timedelta(days=3),
            'location': 'Berlin',
            'signup_type': SignUpType.CREW,
            'signup_is_open': True,
        }
        defaults.update(overrides)
        return Event.objects.create(name=name, **defaults)

    def test_save_generates_slug_from_name_when_missing(self):
        event = self._create_event('Rocktreff 2026', slug='')

        self.assertEqual(event.slug, 'rocktreff-2026')

    def test_get_image_url_returns_placeholder_without_image(self):
        event = self._create_event('Rocktreff 2026')

        self.assertEqual(event.get_image_url(), '/static/assets/4_3_placeholder.webp')

    def test_band_application_open_requires_current_time_within_window(self):
        current_time = timezone.now()
        event = self._create_event(
            'Rocktreff 2026',
            band_application_start=current_time - timedelta(days=1),
            band_application_end=current_time + timedelta(days=1),
        )

        with patch('django.utils.timezone.now', return_value=current_time):
            self.assertTrue(event.band_application_open)

        with patch(
            'django.utils.timezone.now',
            return_value=current_time + timedelta(days=2),
        ):
            self.assertFalse(event.band_application_open)

    def test_exhibitor_application_open_returns_false_without_complete_window(self):
        event = self._create_event('Rocktreff 2026')

        self.assertFalse(event.exhibitor_application_open)

    def test_get_current_event_returns_latest_current_event(self):
        older = self._create_event(
            'Rocktreff 2025',
            slug='rocktreff-2025',
            start_offset_days=-30,
            is_current=True,
        )
        newer = self._create_event(
            'Rocktreff 2026',
            slug='rocktreff-2026',
            is_current=True,
        )

        self.assertEqual(Event.get_current_event(), newer)
        self.assertNotEqual(Event.get_current_event(), older)
