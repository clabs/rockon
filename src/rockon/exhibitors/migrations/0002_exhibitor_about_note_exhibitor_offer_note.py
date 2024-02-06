# Generated by Django 5.0.1 on 2024-02-06 14:09

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rockonexhibitors", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="exhibitor",
            name="about_note",
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="exhibitor",
            name="offer_note",
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
