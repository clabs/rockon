# Generated by Django 5.1 on 2024-08-22 11:08

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rockonbands", "0014_band_is_coverband"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bandmedia",
            name="media_type",
            field=models.CharField(
                choices=[
                    ("unknown", "Unbekannt"),
                    ("audio", "Audio"),
                    ("document", "Dokument"),
                    ("link", "Link"),
                    ("logo", "Logo"),
                    ("press_photo", "Pressefoto"),
                    ("web", "Webseite"),
                ],
                default="unknown",
                max_length=32,
            ),
        ),
    ]
