# Generated by Django 4.1.7 on 2023-03-18 12:22

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0003_event_homepage"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="is_current",
            field=models.BooleanField(default=False),
        ),
    ]
