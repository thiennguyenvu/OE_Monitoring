# Generated by Django 3.0.10 on 2021-03-30 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dj_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DJGroupModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
