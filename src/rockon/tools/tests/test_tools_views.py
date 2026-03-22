from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from rockon.tools.models import LinkShortener


class ToolsViewsTests(TestCase):
    def test_qrcode_generator_renders_page(self):
        response = self.client.get(reverse('tools_qrcode_generator'))

        self.assertEqual(response.status_code, 200)

    def test_link_shortener_redirects_and_increments_counter(self):
        short_link = LinkShortener.objects.create(
            url='https://example.com/target',
            slug='abc123',
            comment='test',
        )

        response = self.client.get(
            reverse('tools_link_shortener', kwargs={'slug': short_link.slug})
        )

        self.assertRedirects(
            response,
            short_link.url,
            fetch_redirect_response=False,
        )
        short_link.refresh_from_db()
        self.assertEqual(short_link.counter, 1)

    def test_link_shortener_returns_404_for_unknown_slug(self):
        response = self.client.get(
            reverse('tools_link_shortener', kwargs={'slug': 'missing'})
        )

        self.assertEqual(response.status_code, 404)

    def test_display_qr_code_renders_for_existing_slug(self):
        short_link = LinkShortener.objects.create(
            url='https://example.com/target',
            slug='qr123',
            comment='qr',
        )

        response = self.client.get(
            reverse('tools_link_shortener_qr', kwargs={'slug': short_link.slug})
        )

        self.assertEqual(response.status_code, 200)

    def test_display_qr_code_returns_404_for_unknown_slug(self):
        response = self.client.get(
            reverse('tools_link_shortener_qr', kwargs={'slug': 'missing'})
        )

        self.assertEqual(response.status_code, 404)
