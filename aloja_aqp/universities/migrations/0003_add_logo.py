from django.db import migrations
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='university',
            name='logo',
            field=cloudinary.models.CloudinaryField(blank=True, null=True, verbose_name='logo'),
        ),
    ]
