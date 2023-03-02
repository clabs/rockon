# Generated by Django 4.1.7 on 2023-03-02 16:30

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models

import event.models.event


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Task",
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
                ("name", models.CharField(max_length=255)),
                ("comment", models.CharField(max_length=511)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Timeline",
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
                ("name", models.CharField(max_length=255)),
                ("comment", models.CharField(max_length=511)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Event",
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
                ("name", models.CharField(max_length=511)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField()),
                ("start", models.DateField(help_text="Veranstaltung beginnt")),
                ("end", models.DateField(help_text="Veranstaltung endet")),
                ("setup_start", models.DateField(help_text="Aufbau beginnt")),
                ("setup_end", models.DateField(help_text="Aufbau endet")),
                ("opening", models.DateField(help_text="Erster Einlass")),
                ("closing", models.DateField(help_text="Ende der Veranstaltung")),
                ("teardown_start", models.DateField(help_text="Abbau beginnt")),
                ("teardown_end", models.DateField(help_text="Abbau endet")),
                ("location", models.CharField(max_length=255)),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=event.models.event.UploadToPathAndRename("events"),
                    ),
                ),
                ("show_on_landing_page", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "sub_event_of",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event.event",
                    ),
                ),
            ],
            options={
                "ordering": ["start"],
            },
        ),
    ]
