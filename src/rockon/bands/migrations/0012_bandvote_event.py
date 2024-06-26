# Generated by Django 5.0.2 on 2024-02-11 16:08

from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rockonbands", "0011_alter_band_options"),
        ("rockonbase", "0006_event_bid_vote_allowed"),
    ]

    operations = [
        migrations.AddField(
            model_name="bandvote",
            name="event",
            field=models.ForeignKey(
                default="428ce37b-e651-4ad8-b82d-cf75939a6eeb",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="band_votes",
                to="rockonbase.event",
            ),
            preserve_default=False,
        ),
    ]
