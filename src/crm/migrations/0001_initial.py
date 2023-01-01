# Generated by Django 4.1.4 on 2023-01-01 17:50

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("event", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LinkShortener",
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
                ("url", models.URLField()),
                ("slug", models.SlugField(unique=True)),
                ("comment", models.TextField()),
                ("counter", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="Organisation",
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
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Sponsoring",
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
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Type",
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
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Person",
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
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("nickname", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("email_verified", models.BooleanField(default=False)),
                ("phone", models.CharField(blank=True, max_length=255, null=True)),
                ("address", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "address_extension",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "address_housenumber",
                    models.SmallIntegerField(blank=True, null=True),
                ),
                ("zip_code", models.CharField(blank=True, max_length=255, null=True)),
                ("place", models.CharField(blank=True, max_length=255, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                ("internal_comment", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("events", models.ManyToManyField(blank=True, to="event.event")),
                (
                    "organisations",
                    models.ManyToManyField(blank=True, to="crm.organisation"),
                ),
            ],
            options={
                "ordering": ["last_name"],
            },
        ),
        migrations.CreateModel(
            name="MagicLink",
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
                ("token", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="magic_links",
                        to="crm.person",
                    ),
                ),
            ],
            options={
                "ordering": ["person", "expires_at"],
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="event.event"
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exhibitors",
                        to="crm.organisation",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="EmailVerification",
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
                ("token", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="email_verifications",
                        to="crm.person",
                    ),
                ),
            ],
            options={
                "ordering": ["person"],
            },
        ),
    ]