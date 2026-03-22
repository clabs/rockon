from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from rockon.base.models import Event
from rockon.base.models.event import SignUpType
from rockon.crew.models import (
    Attendance,
    Crew,
    CrewMember,
    CrewMemberStatus,
    EventTeam,
    Team,
    TeamCategory,
    TeamMember,
    TeamMemberState,
)


class CrewCoordTeamManagementTests(TestCase):
    def setUp(self):
        self.crewcoord_group = Group.objects.create(name='crewcoord')

        self.crewcoord_user = User.objects.create_user(
            username='coord',
            email='coord@example.com',
            password='secret',
            first_name='Coord',
            last_name='User',
        )
        self.crewcoord_user.groups.add(self.crewcoord_group)

        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='secret',
            first_name='Regular',
            last_name='User',
        )

        self.member_user_one = User.objects.create_user(
            username='member-one',
            email='member1@example.com',
            password='secret',
            first_name='Alice',
            last_name='Member',
        )
        self.member_user_two = User.objects.create_user(
            username='member-two',
            email='member2@example.com',
            password='secret',
            first_name='Bob',
            last_name='Member',
        )
        self.member_user_other_event = User.objects.create_user(
            username='member-other',
            email='other@example.com',
            password='secret',
            first_name='Other',
            last_name='Event',
        )

        self.event_one = self._create_event('Rocktreff 2026', 'rocktreff-2026', 0)
        self.event_two = self._create_event('Rocktreff 2027', 'rocktreff-2027', 30)

        self.crew_one = Crew.objects.create(
            event=self.event_one, name='Crew 2026', year=2026
        )
        self.crew_two = Crew.objects.create(
            event=self.event_two, name='Crew 2027', year=2027
        )

        category = TeamCategory.objects.create(
            name='Technik', description='Technikteams'
        )

        self.team_a = Team.objects.create(
            name='Stage',
            description='Stage hands',
            category=category,
            is_public=True,
        )
        self.team_b = Team.objects.create(
            name='Lights',
            description='Lights crew',
            category=category,
            is_public=True,
        )
        self.team_other_event = Team.objects.create(
            name='Awareness',
            description='Awareness crew',
            category=category,
            is_public=True,
        )

        self.event_one_team_a = EventTeam.objects.create(
            event=self.event_one, team=self.team_a
        )
        self.event_one_team_b = EventTeam.objects.create(
            event=self.event_one, team=self.team_b
        )
        self.event_two_team = EventTeam.objects.create(
            event=self.event_two,
            team=self.team_other_event,
        )

        self.crew_member_one = CrewMember.objects.create(
            user=self.member_user_one,
            crew=self.crew_one,
        )
        self.crew_member_two = CrewMember.objects.create(
            user=self.member_user_two,
            crew=self.crew_one,
        )
        self.crew_member_other_event = CrewMember.objects.create(
            user=self.member_user_other_event,
            crew=self.crew_two,
        )

        self.team_member_one = TeamMember.objects.create(
            event_team=self.event_one_team_a,
            crewmember=self.crew_member_one,
            state=TeamMemberState.UNKNOWN,
        )
        self.team_member_two = TeamMember.objects.create(
            event_team=self.event_one_team_a,
            crewmember=self.crew_member_two,
            state=TeamMemberState.CONFIRMED,
        )
        self.team_member_other_event = TeamMember.objects.create(
            event_team=self.event_two_team,
            crewmember=self.crew_member_other_event,
            state=TeamMemberState.UNKNOWN,
        )

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
            signup_type=SignUpType.CREW,
            signup_is_open=True,
        )

    def _url(self, slug: str) -> str:
        return reverse('crew:coord_teams', kwargs={'slug': slug})

    def _members_url(self, slug: str) -> str:
        return reverse('crew:coord_members', kwargs={'slug': slug})

    def _availability_url(self, slug: str) -> str:
        return reverse('crew:coord_availability', kwargs={'slug': slug})

    def test_access_control(self):
        response = self.client.get(self._url(self.event_one.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.regular_user)
        response = self.client.get(self._url(self.event_one.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.crewcoord_user)
        response = self.client.get(self._url(self.event_one.slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Teamverwaltung')

    def test_update_member_state_success_and_cross_event_rejection(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'update_member_state',
                'team_member_id': str(self.team_member_one.id),
                'state': TeamMemberState.CONFIRMED,
            },
        )
        self.assertRedirects(response, self._url(self.event_one.slug))

        self.team_member_one.refresh_from_db()
        self.assertEqual(self.team_member_one.state, TeamMemberState.CONFIRMED)

        other_before = self.team_member_other_event.state
        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'update_member_state',
                'team_member_id': str(self.team_member_other_event.id),
                'state': TeamMemberState.REJECTED,
            },
        )
        self.assertRedirects(response, self._url(self.event_one.slug))

        self.team_member_other_event.refresh_from_db()
        self.assertEqual(self.team_member_other_event.state, other_before)

    def test_modifying_team_membership_is_not_supported(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'move_member',
                'team_member_id': str(self.team_member_one.id),
                'destination_event_team_id': str(self.event_one_team_b.id),
            },
            follow=True,
        )
        self.assertRedirects(response, self._url(self.event_one.slug))
        self.assertContains(response, 'Unbekannte Aktion.')

        self.team_member_one.refresh_from_db()
        self.assertEqual(self.team_member_one.event_team_id, self.event_one_team_a.id)
        self.assertFalse(
            TeamMember.objects.filter(
                event_team=self.event_two_team,
                crewmember=self.crew_member_one,
            ).exists()
        )

    def test_set_team_roles_requires_confirmed_members(self):
        self.client.force_login(self.crewcoord_user)

        self.team_member_one.state = TeamMemberState.CONFIRMED
        self.team_member_one.save(update_fields=['state'])

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'set_team_roles',
                'event_team_id': str(self.event_one_team_a.id),
                'lead_id': str(self.member_user_one.id),
                'vize_lead_id': '',
            },
        )
        self.assertRedirects(response, self._url(self.event_one.slug))

        self.event_one_team_a.refresh_from_db()
        self.assertEqual(self.event_one_team_a.lead_id, self.member_user_one.id)

        self.team_member_one.state = TeamMemberState.UNKNOWN
        self.team_member_one.save(update_fields=['state'])

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'set_team_roles',
                'event_team_id': str(self.event_one_team_a.id),
                'lead_id': str(self.member_user_one.id),
                'vize_lead_id': '',
            },
        )
        self.assertRedirects(response, self._url(self.event_one.slug))

        self.event_one_team_a.refresh_from_db()
        self.assertIsNone(self.event_one_team_a.lead_id)

    def test_set_team_roles_assigns_lead_and_vize_and_rejects_cross_team_vize(self):
        self.client.force_login(self.crewcoord_user)

        self.team_member_one.state = TeamMemberState.CONFIRMED
        self.team_member_one.save(update_fields=['state'])

        external_user = User.objects.create_user(
            username='external-vize',
            email='external-vize@example.com',
            password='secret',
            first_name='External',
            last_name='OnlyTeamB',
        )
        external_crewmember = CrewMember.objects.create(
            user=external_user,
            crew=self.crew_one,
        )
        cross_team_member = TeamMember.objects.create(
            event_team=self.event_one_team_b,
            crewmember=external_crewmember,
            state=TeamMemberState.CONFIRMED,
        )

        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'set_team_roles',
                'event_team_id': str(self.event_one_team_a.id),
                'lead_id': str(self.member_user_one.id),
                'vize_lead_id': str(self.member_user_one.id),
            },
        )
        self.assertRedirects(response, self._url(self.event_one.slug))

        self.event_one_team_a.refresh_from_db()
        self.assertEqual(self.event_one_team_a.lead_id, self.member_user_one.id)
        self.assertEqual(self.event_one_team_a.vize_lead_id, self.member_user_one.id)

        previous_vize_id = self.event_one_team_a.vize_lead_id
        response = self.client.post(
            self._url(self.event_one.slug),
            {
                'action': 'set_team_roles',
                'event_team_id': str(self.event_one_team_a.id),
                'lead_id': str(self.member_user_one.id),
                'vize_lead_id': str(cross_team_member.crewmember.user_id),
            },
            follow=True,
        )
        self.assertRedirects(response, self._url(self.event_one.slug))
        self.assertContains(
            response,
            'Stellvertretung muss ein bestätigtes Teammitglied sein.',
        )

        self.event_one_team_a.refresh_from_db()
        self.assertNotEqual(
            self.event_one_team_a.vize_lead_id,
            cross_team_member.crewmember.user_id,
        )
        self.assertEqual(self.event_one_team_a.vize_lead_id, previous_vize_id)

    def test_coord_members_view_access_control(self):
        response = self.client.get(self._members_url(self.event_one.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.regular_user)
        response = self.client.get(self._members_url(self.event_one.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.crewcoord_user)
        response = self.client.get(self._members_url(self.event_one.slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crewmitglieder')
        self.assertContains(response, 'Alice Member')
        self.assertNotContains(response, 'Other Event')

    def test_coord_members_view_updates_member_state_for_current_event_only(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._members_url(self.event_one.slug),
            {
                'action': 'update_member_state',
                'crew_member_id': str(self.crew_member_one.id),
                'state': 'confirmed',
            },
            follow=True,
        )
        self.assertRedirects(response, self._members_url(self.event_one.slug))
        self.assertContains(response, 'Crewmitgliedsstatus wurde aktualisiert.')

        self.crew_member_one.refresh_from_db()
        self.assertEqual(self.crew_member_one.state, 'confirmed')

        response = self.client.post(
            self._members_url(self.event_one.slug),
            {
                'action': 'update_member_state',
                'crew_member_id': str(self.crew_member_other_event.id),
                'state': 'rejected',
            },
            follow=True,
        )
        self.assertRedirects(response, self._members_url(self.event_one.slug))
        self.assertContains(response, 'Ungültiges Crewmitglied für dieses Event.')

        self.crew_member_other_event.refresh_from_db()
        self.assertEqual(self.crew_member_other_event.state, 'unknown')

    def test_coord_members_view_contains_backstage_link(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.get(self._members_url(self.event_one.slug))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                'admin:rockoncrew_crewmember_change',
                args=[self.crew_member_one.id],
            ),
        )

    def test_coord_members_view_filters_by_name_and_state(self):
        self.client.force_login(self.crewcoord_user)
        self.crew_member_two.state = 'confirmed'
        self.crew_member_two.save(update_fields=['state'])

        response = self.client.get(
            self._members_url(self.event_one.slug),
            {
                'q': 'Bob',
                'state': 'confirmed',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bob Member')
        self.assertNotContains(response, 'Alice Member')
        self.assertNotContains(response, 'Other Event')

    def test_coord_members_update_preserves_active_filters(self):
        self.client.force_login(self.crewcoord_user)

        response = self.client.post(
            self._members_url(self.event_one.slug),
            {
                'action': 'update_member_state',
                'crew_member_id': str(self.crew_member_one.id),
                'state': 'confirmed',
                'q': 'Alice',
                'state_filter': 'unknown',
            },
        )

        expected_url = f'{self._members_url(self.event_one.slug)}?q=Alice&state=unknown'
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    def test_coord_availability_view_access_control(self):
        response = self.client.get(self._availability_url(self.event_one.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.regular_user)
        response = self.client.get(self._availability_url(self.event_one.slug))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.crewcoord_user)
        response = self.client.get(self._availability_url(self.event_one.slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Verfügbarkeit')

    def test_coord_availability_view_shows_confirmed_members_in_day_matrix(self):
        self.client.force_login(self.crewcoord_user)

        setup_day = Attendance.objects.create(
            event=self.event_one,
            day=self.event_one.setup_start,
            phase='setup',
        )
        show_day = Attendance.objects.create(
            event=self.event_one,
            day=self.event_one.opening,
            phase='show',
        )
        Attendance.objects.create(
            event=self.event_two,
            day=self.event_two.opening,
            phase='show',
        )

        self.crew_member_one.state = CrewMemberStatus.CONFIRMED
        self.crew_member_one.save(update_fields=['state'])
        self.crew_member_one.attendance.add(setup_day, show_day)

        self.crew_member_two.state = CrewMemberStatus.CONFIRMED
        self.crew_member_two.save(update_fields=['state'])
        self.crew_member_two.attendance.add(show_day)

        self.crew_member_other_event.state = CrewMemberStatus.CONFIRMED
        self.crew_member_other_event.save(update_fields=['state'])

        response = self.client.get(self._availability_url(self.event_one.slug))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Member')
        self.assertContains(response, 'Bob Member')
        self.assertNotContains(response, 'Other Event')
        self.assertContains(response, setup_day.day.strftime('%d.%m.%Y'))
        self.assertContains(response, show_day.day.strftime('%d.%m.%Y'))
        self.assertContains(response, '2 Tage')
        self.assertContains(response, '1 Tag')
        self.assertContains(response, '2 bestätigt')
        self.assertContains(response, '1 bestätigt')
