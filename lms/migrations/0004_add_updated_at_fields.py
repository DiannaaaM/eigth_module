# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0003_coursesubscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
    ]

