# Generated by Django 4.2.7 on 2023-11-29 20:50

from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rockonbase", "0003_event_band_application_end_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="account_context",
        ),
    ]