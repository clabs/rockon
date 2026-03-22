from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event, Organisation
from rockon.base.models.event import SignUpType
from rockon.exhibitors.models import Asset, Attendance, Exhibitor


class ExhibitorJoinViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='exhibitor-user',
            email='exhibitor@example.com',
            password='secret',
            first_name='Exhi',
            last_name='Bitor',
        )
        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026', 0)

    def _create_event(self, name: str, slug: str, offset_days: int) -> Event:
        start = date(2026, 7, 1) + timedelta(days=offset_days)
        return Event.objects.create(
            name=name,
            slug=slug,
            description=f'{name} description',
            start=start,
            end=start + timedelta(days=2),
            setup_start=start - timedelta(days=2),
            setup_end=start - timedelta(days=1),
            opening=start,
            closing=start + timedelta(days=1),
            teardown_start=start + timedelta(days=2),
            teardown_end=start + timedelta(days=3),
            location='Berlin',
            signup_type=SignUpType.EXHIBITOR,
            signup_is_open=True,
        )

    def test_join_view_redirects_anonymous_users_to_login_request(self):
        response = self.client.get(
            reverse('exhibitors:join', kwargs={'slug': self.event.slug})
        )

        self.assertRedirects(
            response,
            f'{reverse("base:login_request")}?ctx=exhibitors',
            fetch_redirect_response=False,
        )

    def test_join_view_returns_404_for_unknown_event_slug(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('exhibitors:join', kwargs={'slug': 'missing'})
        )

        self.assertEqual(response.status_code, 404)

    @patch(
        'rockon.base.models.user_profile.UserProfile.is_profile_complete_exhibitor',
        return_value=False,
    )
    @patch('rockon.exhibitors.views.join.loader.get_template')
    def test_join_view_uses_profile_incomplete_template_for_incomplete_profile(
        self, get_template, _is_complete
    ):
        self.client.force_login(self.user)
        get_template.return_value.render.return_value = ''

        response = self.client.get(
            reverse('exhibitors:join', kwargs={'slug': self.event.slug})
        )

        self.assertEqual(response.status_code, 200)
        get_template.assert_called_once_with('exhibitor_join_profile_incomplete.html')
        extra_context, request = get_template.return_value.render.call_args.args
        self.assertEqual(extra_context['event'], self.event)
        self.assertEqual(extra_context['slug'], self.event.slug)
        self.assertEqual(request.user, self.user)

    @patch(
        'rockon.base.models.user_profile.UserProfile.is_profile_complete_exhibitor',
        return_value=True,
    )
    @patch('rockon.exhibitors.views.join.loader.get_template')
    def test_join_view_serializes_assets_attendances_and_org_data(
        self, get_template, _is_complete
    ):
        organisation = Organisation.objects.create(
            org_name='Poster Collective',
            org_address='Poster Alley',
            org_house_number='42',
            org_zip='10999',
            org_place='Berlin',
        )
        organisation.members.add(self.user)
        Attendance.objects.create(event=self.event, day=self.event.start)
        Asset.objects.create(name='Power', description='Stromanschluss')

        self.client.force_login(self.user)
        get_template.return_value.render.return_value = ''

        response = self.client.get(
            reverse('exhibitors:join', kwargs={'slug': self.event.slug})
        )

        self.assertEqual(response.status_code, 200)
        get_template.assert_called_once_with('exhibitor_join.html')
        extra_context, request = get_template.return_value.render.call_args.args
        self.assertFalse(extra_context['readonly'])
        self.assertIn('Poster Collective', extra_context['org_json'])
        self.assertIn('Power', extra_context['assets_json'])
        self.assertIn(
            self.event.start.strftime('%d.%m.%Y'),
            extra_context['attendances_json'],
        )
        self.assertEqual(request.user, self.user)

    @patch('rockon.exhibitors.views.join.loader.get_template')
    def test_join_view_sets_readonly_for_existing_submission(self, get_template):
        organisation = Organisation.objects.create(org_name='Readonly Org')
        organisation.members.add(self.user)
        Exhibitor.objects.create(
            event=self.event,
            organisation=organisation,
            offer_note='Prints and zines',
            website='https://example.com',
        )

        self.client.force_login(self.user)
        get_template.return_value.render.return_value = ''

        response = self.client.get(
            reverse('exhibitors:join', kwargs={'slug': self.event.slug})
        )

        self.assertEqual(response.status_code, 200)
        get_template.assert_called_once_with('exhibitor_join.html')
        extra_context, _request = get_template.return_value.render.call_args.args
        self.assertTrue(extra_context['readonly'])
        self.assertEqual(extra_context['site_title'], 'Anmeldung (eingereicht)')
        self.assertIn('Prints and zines', extra_context['exhibitor_json'])
        self.assertIn('Readonly Org', extra_context['org_json'])
