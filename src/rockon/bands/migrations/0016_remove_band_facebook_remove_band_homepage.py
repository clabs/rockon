# Generated by Django 5.1 on 2024-08-22 11:10

from __future__ import annotations

from django.db import migrations


def copy_urls_to_bandmedia(apps, schema_editor):
    Band = apps.get_model("rockonbands", "Band")
    BandMedia = apps.get_model("rockonbands", "BandMedia")
    for band in Band.objects.all():
        if band.facebook:
            BandMedia.objects.create(
                band=band,
                media_type="web",
                url=band.facebook,
            )
        if band.homepage:
            BandMedia.objects.create(
                band=band,
                media_type="web",
                url=band.homepage,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("rockonbands", "0015_alter_bandmedia_media_type"),
    ]

    operations = [
        migrations.RunPython(copy_urls_to_bandmedia),
        migrations.RemoveField(
            model_name="band",
            name="facebook",
        ),
        migrations.RemoveField(
            model_name="band",
            name="homepage",
        ),
    ]
