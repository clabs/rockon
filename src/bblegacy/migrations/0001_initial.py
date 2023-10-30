# Generated by Django 4.2.6 on 2023-10-30 08:02

from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models

import bblegacy.helper


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bid",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=bblegacy.helper.guid,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField()),
                ("modified", models.DateTimeField()),
                ("bandname", models.CharField(blank=True, max_length=255, null=True)),
                ("student", models.BooleanField(default=False)),
                ("managed", models.BooleanField(default=False)),
                ("style", models.CharField(blank=True, max_length=255, null=True)),
                ("letter", models.TextField(blank=True, null=True)),
                ("contact", models.CharField(blank=True, max_length=255, null=True)),
                ("phone", models.CharField(blank=True, max_length=255, null=True)),
                ("mail", models.EmailField(blank=True, max_length=254, null=True)),
                ("url", models.URLField(blank=True, max_length=255, null=True)),
                ("fb", models.URLField(blank=True, max_length=255, null=True)),
            ],
            options={
                "ordering": ["created"],
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=bblegacy.helper.guid,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField()),
                ("modified", models.DateTimeField()),
                ("name", models.CharField(max_length=255)),
                ("opening_date", models.DateTimeField()),
                ("closing_date", models.DateTimeField()),
            ],
            options={
                "ordering": ["opening_date"],
            },
        ),
        migrations.CreateModel(
            name="Region",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=bblegacy.helper.guid,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField()),
                ("modified", models.DateTimeField()),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name": "Region",
                "verbose_name_plural": "Regionen",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=bblegacy.helper.guid,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField()),
                ("modified", models.DateTimeField()),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=255)),
                ("provider", models.CharField(max_length=255)),
                ("role", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Vote",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=bblegacy.helper.guid,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField()),
                ("modified", models.DateTimeField()),
                ("rating", models.IntegerField()),
                (
                    "bid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="bblegacy.bid",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bblegacy.user"
                    ),
                ),
            ],
            options={
                "verbose_name": "Vote",
                "verbose_name_plural": "Votes",
                "ordering": ["bid", "created"],
            },
        ),
        migrations.CreateModel(
            name="Track",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=bblegacy.helper.guid,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField()),
                ("modified", models.DateTimeField()),
                ("name", models.CharField(max_length=255)),
                ("visible", models.BooleanField(default=False)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bblegacy.event"
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=bblegacy.helper.guid,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField()),
                ("modified", models.DateTimeField()),
                ("type", models.CharField(max_length=255)),
                ("text", models.CharField(max_length=255)),
                (
                    "bid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to="bblegacy.bid",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to="bblegacy.user",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Media",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=bblegacy.helper.guid,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField()),
                ("modified", models.DateTimeField()),
                ("type", models.CharField(max_length=255)),
                ("url", models.URLField(blank=True, null=True)),
                ("meta", models.CharField(default=0, max_length=512)),
                ("mimetype", models.CharField(blank=True, max_length=255, null=True)),
                ("filename", models.CharField(blank=True, max_length=255, null=True)),
                ("filesize", models.FloatField(blank=True, null=True)),
                (
                    "bid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media",
                        to="bblegacy.bid",
                    ),
                ),
            ],
            options={
                "verbose_name": "Media",
                "verbose_name_plural": "Medien",
                "ordering": ["bid", "type"],
            },
        ),
        migrations.AddField(
            model_name="event",
            name="tracks",
            field=models.ManyToManyField(
                blank=True, related_name="events", to="bblegacy.track"
            ),
        ),
        migrations.AddField(
            model_name="bid",
            name="event",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="bblegacy.event",
            ),
        ),
        migrations.AddField(
            model_name="bid",
            name="region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bids",
                to="bblegacy.region",
            ),
        ),
        migrations.AddField(
            model_name="bid",
            name="track",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bids",
                to="bblegacy.track",
            ),
        ),
    ]
