from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event
from rockon.base.models.event import SignUpType


class AccountViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='account-user',
            email='account@example.com',
            password='secret',
        )
        self.band_user = User.objects.create_user(
            username='band-user',
            email='band@example.com',
            password='secret',
        )
        self.band_group = Group.objects.create(name='bands')
        self.band_user.groups.add(self.band_group)
        self.crew_user = User.objects.create_user(
            username='crew-user',
            email='crew@example.com',
            password='secret',
        )
        self.crew_group = Group.objects.create(name='crew')
        self.crew_user.groups.add(self.crew_group)
        self.current_event = self._create_event(
            name='Rocktreff 2026',
            slug='rocktreff-2026',
            offset_days=0,
            is_current=True,
        )
        self.fallback_event = self._create_event(
            name='Rocktreff 2027',
            slug='rocktreff-2027',
            offset_days=30,
        )

    def _create_event(
        self,
        *,
        name: str,
        slug: str,
        offset_days: int,
        is_current: bool = False,
    ) -> Event:
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
            signup_type=SignUpType.CREW,
            signup_is_open=True,
            is_current=is_current,
        )

    @patch('rockon.base.views.account.loader.get_template')
    def test_login_request_redirects_authenticated_users_to_account(self, get_template):
        self.client.force_login(self.user)

        response = self.client.get(reverse('base:login_request'))

        self.assertRedirects(
            response,
            reverse('base:account'),
            fetch_redirect_response=False,
        )
        get_template.assert_not_called()

    @patch('rockon.base.views.account.loader.get_template')
    def test_login_request_defaults_context_to_crew(self, get_template):
        get_template.return_value.render.return_value = ''

        response = self.client.get(reverse('base:login_request'))

        self.assertEqual(response.status_code, 200)
        extra_context, request = get_template.return_value.render.call_args.args
        self.assertEqual(extra_context['account_context'], 'crew')
        self.assertEqual(request.user.is_authenticated, False)

    @patch('rockon.base.views.account.loader.get_template')
    def test_logout_renders_template_for_anonymous_users(self, get_template):
        get_template.return_value.render.return_value = ''

        response = self.client.get(reverse('base:logout'))

        self.assertEqual(response.status_code, 200)
        get_template.assert_called_once_with('account/logout.html')

    @patch('rockon.base.views.account.loader.get_template')
    def test_login_token_returns_403_for_unknown_uuid_token(self, get_template):
        get_template.return_value.render.return_value = 'denied'

        response = self.client.get(
            reverse(
                'base:login_token',
                kwargs={'token': '00000000-0000-0000-0000-000000000000'},
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'denied', status_code=403)

    @patch('rockon.base.views.account.loader.get_template')
    @patch('rockon.base.views.account.authenticate')
    def test_login_token_returns_403_when_no_event_exists(
        self, authenticate, get_template
    ):
        Event.objects.all().delete()
        authenticate.return_value = self.user
        get_template.return_value.render.return_value = 'no-event'

        response = self.client.get(
            reverse('base:login_token', kwargs={'token': 'magic-token'})
        )

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'no-event', status_code=403)

    @patch('rockon.base.views.account.authenticate')
    def test_login_token_redirects_users_without_groups_to_context_selection(
        self, authenticate
    ):
        authenticate.return_value = self.user

        response = self.client.get(
            reverse('base:login_token', kwargs={'token': 'magic-token'})
        )

        self.assertRedirects(
            response,
            reverse('base:select_context'),
            fetch_redirect_response=False,
        )

    @patch('rockon.base.views.account.get_fallback_event_for_user')
    @patch('rockon.base.views.account.authenticate')
    def test_login_token_redirects_band_users_to_fallback_event(
        self, authenticate, get_fallback_event_for_user
    ):
        authenticate.return_value = self.band_user
        get_fallback_event_for_user.return_value = self.fallback_event

        response = self.client.get(
            reverse('base:login_token', kwargs={'token': 'magic-token'})
        )

        self.assertRedirects(
            response,
            reverse(
                'bands:bid_router',
                kwargs={'slug': self.fallback_event.slug},
            ),
            fetch_redirect_response=False,
        )

    @patch('rockon.base.views.account.authenticate')
    def test_login_token_redirects_non_band_users_to_home(self, authenticate):
        authenticate.return_value = self.crew_user

        response = self.client.get(
            reverse('base:login_token', kwargs={'token': 'magic-token'})
        )

        self.assertRedirects(
            response,
            reverse('crm_user_home'),
            fetch_redirect_response=False,
        )

    @patch('rockon.base.views.account.loader.get_template')
    def test_account_created_renders_template(self, get_template):
        get_template.return_value.render.return_value = ''

        response = self.client.get(reverse('base:account_created'))

        self.assertEqual(response.status_code, 200)
        get_template.assert_called_once_with('account/created.html')

    @patch('rockon.base.views.account.loader.get_template')
    def test_verify_email_renders_template_with_token(self, get_template):
        get_template.return_value.render.return_value = ''

        response = self.client.get(
            reverse('base:verify_email', kwargs={'token': 'verify-token'})
        )

        self.assertEqual(response.status_code, 200)
        extra_context, _request = get_template.return_value.render.call_args.args
        self.assertEqual(extra_context['token'], 'verify-token')

    @patch('rockon.base.views.account.loader.get_template')
    def test_select_context_renders_template(self, get_template):
        get_template.return_value.render.return_value = ''

        response = self.client.get(reverse('base:select_context'))

        self.assertEqual(response.status_code, 200)
        get_template.assert_called_once_with('account/select_context.html')
