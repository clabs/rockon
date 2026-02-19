from django.db import migrations


def fix_corrupted_bid_status(apps, schema_editor):
    Band = apps.get_model('rockonbands', 'Band')
    Band.objects.filter(bid_status='lineupLine Up').update(bid_status='lineup')


class Migration(migrations.Migration):
    dependencies = [
        ('rockonbands', '0021_alter_band_bid_status'),
    ]

    operations = [
        migrations.RunPython(fix_corrupted_bid_status, migrations.RunPython.noop),
    ]
