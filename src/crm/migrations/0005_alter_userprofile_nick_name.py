# Generated by Django 4.2 on 2023-04-20 16:16

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crm", "0004_alter_userprofile_address_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="nick_name",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
