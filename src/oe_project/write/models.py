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
    date = models.DateTimeField(default=now)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True)
    model = models.ForeignKey(DJModel, on_delete=models.CASCADE, null=True)
    version = models.PositiveIntegerField()
    shift_work = models.BooleanField(default=False)
    qty_plan = models.PositiveIntegerField()

class Planning(models.Model):
    timestamp = models.FloatField()
    date = models.CharField(max_length=10)
    time = models.CharField(max_length=10)
    department = models.CharField(max_length=3)
    line = models.CharField(max_length=1)
    group_model = models.CharField(max_length=100)
    version = models.PositiveIntegerField()
    shift_work = models.BooleanField()
    qty_plan = models.PositiveIntegerField()

class Friend(models.Model):
    nickname = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    likes = models.CharField(max_length=250, null=True, blank=True)
    dob = models.DateField(auto_now_add=False, null=True, blank=True)
    lives_in = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.nickname
