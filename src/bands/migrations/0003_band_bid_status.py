# Generated by Django 4.2.7 on 2023-11-05 22:43

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bands", "0002_band_are_students_band_cover_letter_band_facebook_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="band",
            name="bid_status",
            field=models.CharField(
                choices=[
                    ("unknown", "Unbekannt"),
                    ("pending", "Bearbeitung"),
                    ("accepted", "Angenommen"),
                    ("declined", "Abgelehnt"),
                ],
                default="unknown",
                max_length=32,
            ),
        ),
    ]