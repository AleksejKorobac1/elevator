# Generated by Django 3.1.4 on 2020-12-03 09:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elevatormain', '0009_auto_20201203_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='destination',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='log',
            name='position',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='log',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 3, 11, 39, 54)),
        ),
    ]
