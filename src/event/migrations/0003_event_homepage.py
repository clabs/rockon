# Generated by Django 4.1.7 on 2023-03-08 20:18

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0002_event_signup_is_open_event_signup_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="url",
            field=models.URLField(blank=True, null=True),
        ),
    ]