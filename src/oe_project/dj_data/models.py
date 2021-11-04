from django.db import models

# Create your models here.


class Department(models.Model):
    DEPT_NAME = (
        ('ARM', 'ARM'), 
        ('ASS', 'ASS'), 
    )
    name = models.CharField(max_length=3, choices=DEPT_NAME)

    def __str__(self):
        return self.name


class Line(models.Model):
    LINE_NAME = (
        ('A', 'A'), ('B', 'B'), ('C', 'C'), 
        ('D', 'D'), ('E', 'E'), ('F', 'F'), 
        ('J', 'J'), 
    )
    name = models.CharField(max_length=1, choices=LINE_NAME)

    def __str__(self):
        return self.name


class DJModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name}-{self.description}"

class DJProcess(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    model = models.ForeignKey(DJModel, on_delete=models.CASCADE, null=True)
    st = models.FloatField(default=22)
    description = models.CharField(max_length=100, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Dj processes"

    def __str__(self):
        return f"{self.name}-{self.description}"
