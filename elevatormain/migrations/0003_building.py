# Generated by Django 3.1.4 on 2020-12-01 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elevatormain', '0002_auto_20201201_1719'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('floor_count', models.IntegerField(default=2)),
            ],
        ),
    ]
