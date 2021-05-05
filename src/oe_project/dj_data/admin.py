from django.contrib import admin

# Register your models here.
from .models import *

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    DEPT_NAME = (
        ('ARM', 'ARM'),
        ('ASS', 'ASS'),
    )
    name = models.CharField(max_length=3, choices=DEPT_NAME)
    search_fields = ('id', 'name',)

@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    LINE_NAME = (
        ('A', 'A'), ('B', 'B'), ('C', 'C'),
        ('D', 'D'), ('E', 'E'), ('F', 'F'),
        ('J', 'J'),
    )
    name = models.CharField(max_length=1, choices=LINE_NAME)
    search_fields = ('id', 'name')

@admin.register(DJGroupModel)
class DJGroupModelAdmin(admin.ModelAdmin):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    search_fields = ('id', 'name', 'description')

@admin.register(DJModel)
class DJModelAdmin(admin.ModelAdmin):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(
        DJGroupModel, on_delete=models.CASCADE, null=True)
    st = models.FloatField(default=22)
    description = models.CharField(max_length=100, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    search_fields = ('id', 'name', 'department__name', 'group__description', 'st', 'description', 'order' )
