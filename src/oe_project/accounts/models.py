from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import NullBooleanField

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE = (
        ('Guest', 'Guest'),
        ('Planner', 'Planner'),
        ('Tester', 'Tester'),
    )
    roles = models.CharField(max_length=25, choices=ROLE, default='Guest')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=f'avatar')