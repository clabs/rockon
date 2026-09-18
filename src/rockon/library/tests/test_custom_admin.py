from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import SimpleTestCase

from rockon.library.custom_admin import CustomAdminModel


class CustomAdminModelTests(SimpleTestCase):
    def test_base_readonly_fields_are_always_present(self):
        class PlainAdmin(CustomAdminModel):
            pass

        instance = PlainAdmin(User, admin.site)
        self.assertEqual(instance.readonly_fields, ['created_at', 'updated_at', 'id'])

    def test_subclass_fields_are_kept_and_deduplicated(self):
        class CustomFieldsAdmin(CustomAdminModel):
            readonly_fields = ('name', 'created_at')

        instance = CustomFieldsAdmin(User, admin.site)
        self.assertEqual(
            instance.readonly_fields,
            ['name', 'created_at', 'updated_at', 'id'],
        )
