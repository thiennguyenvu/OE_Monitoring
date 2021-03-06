# Generated by Django 3.0.10 on 2021-03-30 08:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dj_data', '0004_djmodel_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('likes', models.CharField(blank=True, max_length=250, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('lives_in', models.CharField(blank=True, max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Planning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.FloatField()),
                ('date', models.CharField(max_length=10)),
                ('time', models.CharField(max_length=10)),
                ('department', models.CharField(max_length=100)),
                ('line', models.CharField(max_length=1)),
                ('group', models.CharField(max_length=100)),
                ('version', models.PositiveIntegerField()),
                ('shift_work', models.BooleanField()),
                ('qty_plan', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='WriteData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.BooleanField(default=False)),
                ('qty_actual', models.PositiveIntegerField()),
                ('timestamps', models.FloatField()),
                ('machine', models.BooleanField(default=True)),
                ('material', models.BooleanField(default=True)),
                ('quality', models.BooleanField(default=True)),
                ('other', models.BooleanField(default=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('version', models.PositiveIntegerField()),
                ('shift_work', models.BooleanField(default=False)),
                ('qty_plan', models.PositiveIntegerField()),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dj_data.Department')),
                ('line', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dj_data.Line')),
                ('model', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dj_data.DJModel')),
            ],
        ),
    ]
