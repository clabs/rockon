# Generated by Django 4.1.7 on 2023-03-01 15:42

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import library.uploadandpathrename


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("event", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendance",
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
                ("day", models.DateField()),
                (
                    "phase",
                    models.CharField(
                        choices=[
                            ("setup", "Aufbau"),
                            ("show", "Veranstaltung"),
                            ("teardown", "Abbau"),
                        ],
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="event.event"
                    ),
                ),
            ],
            options={
                "ordering": ["day"],
            },
        ),
        migrations.CreateModel(
            name="Crew",
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
                ("year", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="crews",
                        to="event.event",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CrewMember",
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
                ("birthday", models.DateField(null=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("unknown", "Unbekannt"),
                            ("confirmed", "Bestätigt"),
                            ("rejected", "Abgelehnt"),
                            ("arrived", "Angekommen"),
                        ],
                        default="unknown",
                        max_length=12,
                    ),
                ),
                (
                    "nutrition",
                    models.CharField(
                        choices=[
                            ("vegan", "Vegan"),
                            ("vegetarian", "Vegetarisch"),
                            ("omnivore", "Omnivor"),
                        ],
                        max_length=12,
                        null=True,
                    ),
                ),
                ("nutrition_note", models.TextField(blank=True, null=True)),
                ("skills_note", models.TextField(blank=True, null=True)),
                ("attendance_note", models.TextField(blank=True, null=True)),
                ("stays_overnight", models.BooleanField(default=False)),
                ("general_note", models.TextField(blank=True, null=True)),
                ("is_adult", models.BooleanField(default=False)),
                ("needs_leave_of_absence", models.BooleanField(default=False)),
                ("has_leave_of_absence", models.BooleanField(default=False)),
                ("leave_of_absence_note", models.TextField(blank=True, null=True)),
                ("internal_note", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "attendance",
                    models.ManyToManyField(blank=True, to="crew.attendance"),
                ),
                (
                    "crew",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="crew.crew"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Shirt",
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
                (
                    "size",
                    models.CharField(
                        choices=[
                            ("S", "S"),
                            ("M", "M"),
                            ("L", "L"),
                            ("XL", "XL"),
                            ("2XL", "2XL"),
                            ("3XL", "3XL"),
                        ],
                        max_length=12,
                    ),
                ),
                (
                    "cut",
                    models.CharField(
                        choices=[("straight", "Regulär"), ("fitted", "Figurbetont")],
                        max_length=12,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["cut", "size"],
            },
        ),
        migrations.CreateModel(
            name="Skill",
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
                ("explanation", models.CharField(max_length=511)),
                (
                    "icon",
                    models.CharField(
                        default="heart",
                        help_text='<a target="_blank" href="https://semantic-ui.com/elements/icon.html">Wähle ein Icon aus</a>',
                        max_length=255,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Team",
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
                (
                    "contact_mail",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                ("is_public", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "lead",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lead",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vize_lead",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vize_lead",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="TeamMember",
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
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("unknown", "Unbekannt"),
                            ("confirmed", "Bestätigt"),
                            ("rejected", "Abgelehnt"),
                        ],
                        default="unknown",
                        max_length=12,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "crewmember",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teams",
                        to="crew.crewmember",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="crew.team",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="crewmember",
            name="shirt",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="crewmember_shirt",
                to="crew.shirt",
            ),
        ),
        migrations.AddField(
            model_name="crewmember",
            name="skills",
            field=models.ManyToManyField(blank=True, to="crew.skill"),
        ),
        migrations.AddField(
            model_name="crewmember",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
