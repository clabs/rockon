# Generated by Django 4.2.7 on 2023-12-02 15:28

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rockonbase", "0005_delete_accountcontext_alter_event_signup_is_open"),
        ("rockonbands", "0002_alter_band_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="band",
            name="repeated",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="Track",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "slug",
                    models.SlugField(blank=True, default=None, null=True, unique=True),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "events",
                    models.ManyToManyField(
                        blank=True,
                        default=None,
                        related_name="tracks",
                        to="rockonbase.event",
                    ),
                ),
            ],
            options={
                "verbose_name": "Track",
                "verbose_name_plural": "Tracks",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="band",
            name="track",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bands",
                to="rockonbands.track",
            ),
        ),
    ]
