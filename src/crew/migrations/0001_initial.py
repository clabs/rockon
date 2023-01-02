# Generated by Django 4.1.4 on 2023-01-02 11:13

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models

import crew.models.team


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("crm", "0001_initial"),
        ("event", "0001_initial"),
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
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="event.event"
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
                ("comment", models.CharField(blank=True, max_length=511, null=True)),
                ("explanation", models.CharField(max_length=511)),
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
                        upload_to=crew.models.team.UploadToPathAndRename("teams"),
                    ),
                ),
                ("is_public", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "lead",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lead",
                        to="crm.person",
                    ),
                ),
                (
                    "vize_lead",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vize_lead",
                        to="crm.person",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
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
                ("birthday", models.DateField()),
                (
                    "nutrition",
                    models.CharField(
                        choices=[
                            ("vegan", "Vegan"),
                            ("vegetarian", "Vegetarisch"),
                            ("omnivore", "Omnivor"),
                        ],
                        max_length=12,
                    ),
                ),
                (
                    "nutrition_note",
                    models.CharField(blank=True, max_length=511, null=True),
                ),
                (
                    "skills_note",
                    models.CharField(blank=True, max_length=1023, null=True),
                ),
                (
                    "attendance_note",
                    models.CharField(blank=True, max_length=1023, null=True),
                ),
                ("overnight", models.BooleanField(default=False)),
                (
                    "general_note",
                    models.CharField(blank=True, max_length=1023, null=True),
                ),
                ("is_underaged", models.BooleanField(default=True)),
                ("needs_leave_of_absence", models.BooleanField(default=False)),
                ("has_leave_of_absence", models.BooleanField(default=False)),
                (
                    "leave_of_absence_note",
                    models.CharField(blank=True, max_length=1023, null=True),
                ),
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
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="crm.person"
                    ),
                ),
                (
                    "shirt",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="crewmember_shirt",
                        to="crew.shirt",
                    ),
                ),
                ("skills", models.ManyToManyField(blank=True, to="crew.skill")),
                ("teams", models.ManyToManyField(blank=True, to="crew.team")),
            ],
        ),
    ]
