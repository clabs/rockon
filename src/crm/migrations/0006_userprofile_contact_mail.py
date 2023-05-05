# Generated by Django 4.2 on 2023-04-30 13:34

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crm", "0005_alter_userprofile_nick_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="contact_mail",
            field=models.EmailField(
                blank=True, default=None, max_length=1024, null=True
            ),
        ),
    ]