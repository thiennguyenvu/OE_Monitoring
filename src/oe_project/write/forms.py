from django import forms
from django.forms import ModelForm
from .models import models, DJModel, Department, Line, DJGroupModel
import datetime

class DateInput(forms.DateInput):
    input_type = 'date'

class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
    
class LineForm(ModelForm):
    class Meta:
        model = Line
        fields = '__all__'

class DJGroupModelForm(ModelForm):
    class Meta:
        model = DJGroupModel
        fields = '__all__'
