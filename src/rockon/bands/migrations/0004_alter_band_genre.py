# Generated by Django 5.0 on 2023-12-06 09:28

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rockonbands", "0003_band_repeated_track_band_track"),
    ]

    operations = [
        migrations.AlterField(
            model_name="band",
            name="genre",
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),
    ]
