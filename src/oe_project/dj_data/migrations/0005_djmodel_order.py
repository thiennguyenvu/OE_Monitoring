# Generated by Django 3.0.10 on 2021-04-09 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dj_data', '0004_djmodel_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='djmodel',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
