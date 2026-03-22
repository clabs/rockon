from __future__ import annotations

from datetime import date as real_date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profile-user',
            email='profile@example.com',
            password='secret',
        )
        self.profile = self.user.profile

    def test_user_profile_is_created_automatically(self):
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)

    def test_full_name_falls_back_to_email_when_names_are_missing(self):
        self.assertEqual(self.profile.full_name, 'profile@example.com')

        self.user.email = ''
        self.user.save(update_fields=['email'])

        self.assertEqual(self.profile.full_name, 'profile-user')

    def test_profile_complete_crew_requires_all_contact_fields(self):
        self.user.first_name = 'Crew'
        self.user.last_name = 'Member'
        self.user.save(update_fields=['first_name', 'last_name'])
        self.profile.phone = '030123456'
        self.profile.address = 'Teststrasse'
        self.profile.address_housenumber = '42'
        self.profile.zip_code = '10999'
        self.profile.place = 'Berlin'
        self.profile.birthday = real_date(1990, 1, 1)
        self.profile.save()

        self.assertTrue(self.profile.is_profile_complete_crew())

        self.profile.phone = ''
        self.profile.save(update_fields=['phone'])

        self.assertFalse(self.profile.is_profile_complete_crew())

    def test_profile_complete_band_and_exhibitor_require_basic_contact_fields(self):
        self.user.first_name = 'Book'
        self.user.last_name = 'Able'
        self.user.save(update_fields=['first_name', 'last_name'])
        self.profile.phone = '030123456'
        self.profile.save(update_fields=['phone'])

        self.assertTrue(self.profile.is_profile_complete_band())
        self.assertTrue(self.profile.is_profile_complete_exhibitor())

        self.profile.phone = ''
        self.profile.save(update_fields=['phone'])

        self.assertFalse(self.profile.is_profile_complete_band())
        self.assertFalse(self.profile.is_profile_complete_exhibitor())

    def test_age_helpers_respect_birthdays(self):
        self.profile.birthday = real_date(2009, 3, 22)

        with patch('rockon.base.models.user_profile.date') as mock_date:
            mock_date.today.return_value = real_date(2026, 3, 22)
            self.assertTrue(self.profile.over_16())
            self.assertFalse(self.profile.over_18())

        self.profile.birthday = real_date(2008, 3, 23)

        with patch('rockon.base.models.user_profile.date') as mock_date:
            mock_date.today.return_value = real_date(2026, 3, 22)
            self.assertFalse(self.profile.over_18())

        self.profile.birthday = real_date(2008, 3, 22)

        with patch('rockon.base.models.user_profile.date') as mock_date:
            mock_date.today.return_value = real_date(2026, 3, 22)
            self.assertTrue(self.profile.over_18())
