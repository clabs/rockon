# Generated by Django 4.2.7 on 2023-11-26 19:41

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "rockonbase",
            "0002_accountcontext_remove_userprofile_account_context_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="band_application_end",
            field=models.DateTimeField(
                blank=True, help_text="Bandbewerbung endet", null=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="band_application_start",
            field=models.DateTimeField(
                blank=True, help_text="Bandbewerbung beginnt", null=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="exhibitor_application_end",
            field=models.DateTimeField(
                blank=True, help_text="Ausstellerbewerbung endet", null=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="exhibitor_application_start",
            field=models.DateTimeField(
                blank=True, help_text="Ausstellerbewerbung beginnt", null=True
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="signup_is_open",
            field=models.BooleanField(
                default=True, help_text="Crew Anmeldung ist offen"
            ),
        ),
    ]
