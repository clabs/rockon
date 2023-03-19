# Generated by Django 4.1.7 on 2023-03-19 12:28

from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0004_event_is_current"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="sub_event_of",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sub_events",
                to="event.event",
            ),
        ),
    ]