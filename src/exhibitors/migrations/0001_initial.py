# Generated by Django 4.1.5 on 2023-01-22 19:53

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("crm", "0001_initial"),
        ("event", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Asset",
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
                ("explanation", models.TextField(blank=True)),
                ("is_bool", models.BooleanField(default=False)),
                (
                    "icon",
                    models.CharField(
                        default="heart",
                        help_text='<a target="_blank" href="https://semantic-ui.com/elements/icon.html">Wähle ein Icon aus</a>',
                        max_length=255,
                    ),
                ),
                ("internal_comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
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
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exhibitor_attendances",
                        to="event.event",
                    ),
                ),
            ],
            options={
                "ordering": ["day"],
            },
        ),
        migrations.CreateModel(
            name="Exhibitor",
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
                ("is_confirmed", models.BooleanField(default=False)),
                (
                    "market_id",
                    models.CharField(
                        blank=True, max_length=255, null=True, unique=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "attendance",
                    models.ManyToManyField(blank=True, to="exhibitors.attendance"),
                ),
                (
                    "event",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="event.event"
                    ),
                ),
                (
                    "organization",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exhibitor",
                        to="crm.organisation",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ExhibitorAttendance",
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
                ("users_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "day",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exhibitors",
                        to="exhibitors.attendance",
                    ),
                ),
                (
                    "exhibitor",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendance_count",
                        to="exhibitors.exhibitor",
                    ),
                ),
            ],
            options={
                "ordering": ["exhibitor"],
            },
        ),
        migrations.CreateModel(
            name="ExhibitorAsset",
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
                ("is_checked", models.BooleanField(blank=True, null=True)),
                ("count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "asset",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exhibitor",
                        to="exhibitors.asset",
                    ),
                ),
                (
                    "exhibitor",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="asset",
                        to="exhibitors.exhibitor",
                    ),
                ),
            ],
            options={
                "ordering": ["asset"],
            },
        ),
    ]
