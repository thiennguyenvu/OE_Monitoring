from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Department)
admin.site.register(Line)
admin.site.register(DJGroupModel)
admin.site.register(DJModel)