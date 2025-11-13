# Generated migration to add route JSONField to UniversityDistance
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accommodations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='universitydistance',
            name='route',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
