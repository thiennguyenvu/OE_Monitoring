from django.db import models
from django.utils.timezone import now
from dj_data.models import *
# Create your models here.


class WriteData(models.Model):
    start = models.BooleanField(default=False)
    qty_actual = models.PositiveIntegerField()
    timestamps = models.FloatField()
    machine = models.BooleanField(default=True)
    material = models.BooleanField(default=True)
    quality = models.BooleanField(default=True)
    other = models.BooleanField(default=True)
    date = models.CharField(max_length=10)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True)
    process = models.ForeignKey(DJProcess, on_delete=models.CASCADE, null=True)
    version = models.PositiveIntegerField()
    shift_work = models.BooleanField(default=False)
    qty_plan = models.PositiveIntegerField()


class Planning(models.Model):
    timestamp = models.FloatField()
    date = models.CharField(max_length=10)
    time = models.CharField(max_length=10)
    department = models.CharField(max_length=3)
    line = models.CharField(max_length=1)
    model = models.CharField(max_length=100)
    version = models.PositiveIntegerField()
    shift_work = models.BooleanField()
    qty_plan = models.PositiveIntegerField()


class LatestData(models.Model):
    start = models.BooleanField(default=False)
    qty_actual = models.PositiveIntegerField()
    timestamps = models.FloatField()
    machine = models.BooleanField(default=True)
    material = models.BooleanField(default=True)
    quality = models.BooleanField(default=True)
    other = models.BooleanField(default=True)
    date = models.CharField(max_length=10)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True)
    process = models.ForeignKey(DJProcess, on_delete=models.CASCADE, null=True)
    version = models.PositiveIntegerField()
    shift_work = models.BooleanField(default=False)
    qty_plan = models.PositiveIntegerField()
