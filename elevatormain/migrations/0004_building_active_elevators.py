# Generated by Django 3.1.4 on 2020-12-02 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elevatormain', '0003_building'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='active_elevators',
            field=models.IntegerField(default=2),
        ),
    ]
