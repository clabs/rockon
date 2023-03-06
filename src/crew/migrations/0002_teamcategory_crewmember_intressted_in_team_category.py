# Generated by Django 4.1.7 on 2023-03-06 22:43

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models

import library.uploadandpathrename


class Migration(migrations.Migration):
    dependencies = [
        ("crew", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeamCategory",
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
                ("name", models.CharField(max_length=1024)),
                ("description", models.TextField()),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=library.uploadandpathrename.UploadToPathAndRename(
                            "teams"
                        ),
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Team categories",
            },
        ),
        migrations.AddField(
            model_name="crewmember",
            name="intressted_in",
            field=models.ManyToManyField(blank=True, to="crew.teamcategory"),
        ),
        migrations.AddField(
            model_name="team",
            name="category",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="teams",
                to="crew.teamcategory",
            ),
        ),
    ]
