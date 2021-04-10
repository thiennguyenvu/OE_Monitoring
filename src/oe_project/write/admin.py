from django.contrib import admin

# Register your models here.
from .models import WriteData, Planning

admin.site.register(WriteData)
admin.site.register(Planning)