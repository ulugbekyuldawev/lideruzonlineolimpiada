# Generated manually for question images
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olympiad', '0004_branch_dynamic'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
