# Generated by Django 4.1.7 on 2023-03-08 16:28

from __future__ import annotations

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("event", "0002_event_signup_is_open_event_signup_type_and_more"),
        ("crm", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="organisation",
            options={"ordering": ["org_name"]},
        ),
        migrations.RenameField(
            model_name="organisation",
            old_name="name",
            new_name="org_name",
        ),
        migrations.RemoveField(
            model_name="organisation",
            name="comment",
        ),
        migrations.RemoveField(
            model_name="organisation",
            name="contact_user",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="organisations",
        ),
        migrations.AddField(
            model_name="organisation",
            name="internal_comment",
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="members",
            field=models.ManyToManyField(
                default=None, related_name="organisations", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="organisation",
            name="org_address",
            field=models.CharField(default=None, max_length=511, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="org_address_extension",
            field=models.CharField(default=None, max_length=511, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="org_house_number",
            field=models.CharField(default=None, max_length=31, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="org_place",
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="org_zip",
            field=models.CharField(default=None, max_length=31, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="address",
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="address_extension",
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="address_housenumber",
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="comment",
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="events",
            field=models.ManyToManyField(default=None, to="event.event"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="internal_comment",
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="phone",
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="place",
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="zip_code",
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
