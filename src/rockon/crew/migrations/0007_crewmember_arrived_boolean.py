from django.db import migrations, models


def promote_arrived_to_confirmed(apps, schema_editor):
    CrewMember = apps.get_model('rockoncrew', 'CrewMember')
    CrewMember.objects.filter(state='arrived').update(state='confirmed', arrived=True)


class Migration(migrations.Migration):
    dependencies = [
        ('rockoncrew', '0006_eventteam_refactor'),
    ]

    operations = [
        migrations.AddField(
            model_name='crewmember',
            name='arrived',
            field=models.BooleanField(db_default=False, default=False),
        ),
        migrations.RunPython(
            promote_arrived_to_confirmed,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='crewmember',
            name='state',
            field=models.CharField(
                choices=[
                    ('unknown', 'Unbekannt'),
                    ('confirmed', 'Bestätigt'),
                    ('rejected', 'Abgelehnt'),
                ],
                db_default='unknown',
                default='unknown',
                max_length=12,
            ),
        ),
    ]
