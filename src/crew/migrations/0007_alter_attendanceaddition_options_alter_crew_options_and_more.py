# Generated by Django 4.2.7 on 2023-11-04 11:52

from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("crew", "0006_rename_intressted_in_crewmember_interested_in"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="attendanceaddition",
            options={"ordering": ["created_at"]},
        ),
        migrations.AlterModelOptions(
            name="crew",
            options={"ordering": ["created_at"]},
        ),
        migrations.AlterModelOptions(
            name="crewmember",
            options={"ordering": ["created_at"]},
        ),
        migrations.AlterModelOptions(
            name="teammember",
            options={"ordering": ["created_at"]},
        ),
    ]
