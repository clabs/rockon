from __future__ import annotations

import json
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event
from rockon.crew.models import (
    Crew,
    CrewMember,
    CrewMemberStatus,
    EventTeam,
    Team,
    TeamCategory,
)


class JoinViewTests(TestCase):
    def setUp(self):
        self.event = self._create_event('Rocktreff 2026', 'rocktreff-2026')
        self.user = User.objects.create_user(
            username='crew-applicant',
            email='applicant@example.com',
            password='secret',
            first_name='Ada',
            last_name='Applicant',
        )

    def _create_event(self, name: str, slug: str) -> Event:
        start = date(2026, 7, 1)
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
        )

    def _complete_profile(self):
        profile = self.user.profile
        profile.phone = '0123456789'
        profile.address = 'Teststr.'
        profile.address_housenumber = '1'
        profile.zip_code = '12345'
        profile.place = 'Berlin'
        profile.birthday = date(1990, 1, 1)
        profile.save()

    def _url(self, slug: str) -> str:
        return reverse('crew:join', kwargs={'slug': slug})

    def test_unauthenticated_redirects_to_login_with_crew_context(self):
        response = self.client.get(self._url(self.event.slug))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'{reverse("base:login_request")}?ctx=crew')

    def test_unknown_event_slug_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(self._url('missing'))
        self.assertEqual(response.status_code, 404)

    @patch('rockon.crew.views.join.loader.get_template')
    def test_incomplete_profile_renders_incomplete_template(self, get_template):
        self.client.force_login(self.user)
        get_template.return_value.render.return_value = ''

        response = self.client.get(self._url(self.event.slug))

        self.assertEqual(response.status_code, 200)
        get_template.assert_any_call('join_profile_incomplete.html')
        extra_context, _request = get_template.return_value.render.call_args.args
        self.assertEqual(
            extra_context['site_title'], 'Profil unvollständig - Crewanmeldung'
        )

    @patch('rockon.crew.views.join.loader.get_template')
    def test_complete_profile_no_existing_signup_renders_empty_form(self, get_template):
        self._complete_profile()
        self.client.force_login(self.user)
        get_template.return_value.render.return_value = ''

        response = self.client.get(self._url(self.event.slug))

        self.assertEqual(response.status_code, 200)
        extra_context, _request = get_template.return_value.render.call_args.args
        self.assertEqual(extra_context['crew_member_state'], '')
        self.assertFalse(extra_context['form_is_readonly'])
        initial_form_data = json.loads(extra_context['initial_form_data_json'])
        self.assertEqual(initial_form_data['crew_shirt'], '')
        self.assertEqual(initial_form_data['skill_ids'], [])

    @patch('rockon.crew.views.join.loader.get_template')
    def test_confirmed_signup_is_readonly(self, get_template):
        self._complete_profile()
        self.client.force_login(self.user)
        get_template.return_value.render.return_value = ''

        crew = Crew.objects.create(event=self.event, name='Crew 2026', year=2026)
        CrewMember.objects.create(
            user=self.user, crew=crew, state=CrewMemberStatus.CONFIRMED
        )

        response = self.client.get(self._url(self.event.slug))

        self.assertEqual(response.status_code, 200)
        extra_context, _request = get_template.return_value.render.call_args.args
        self.assertEqual(extra_context['crew_member_state'], CrewMemberStatus.CONFIRMED)
        self.assertTrue(extra_context['form_is_readonly'])

    @patch('rockon.crew.views.join.loader.get_template')
    def test_team_categories_json_only_includes_public_teams_for_event(
        self, get_template
    ):
        self._complete_profile()
        self.client.force_login(self.user)
        get_template.return_value.render.return_value = ''

        category = TeamCategory.objects.create(name='Aufbau', description='desc')
        public_team = Team.objects.create(
            name='Bühnenbau',
            description='desc',
            category=category,
            is_public=True,
        )
        private_team = Team.objects.create(
            name='Orga intern',
            description='desc',
            category=category,
            is_public=False,
        )
        EventTeam.objects.create(event=self.event, team=public_team)
        EventTeam.objects.create(event=self.event, team=private_team)

        response = self.client.get(self._url(self.event.slug))

        self.assertEqual(response.status_code, 200)
        extra_context, _request = get_template.return_value.render.call_args.args
        team_categories = json.loads(extra_context['team_categories_json'])
        self.assertEqual(len(team_categories), 1)
        team_names = [team['name'] for team in team_categories[0]['teams']]
        self.assertEqual(team_names, ['Bühnenbau'])
