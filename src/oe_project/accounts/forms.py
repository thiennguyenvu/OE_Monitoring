from django import forms
from django.forms import ModelForm
from .models import *


class UserBioForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('bio',)


class UserAvatarForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('avatar',)


class UserProfileForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email',)
        widgets = {
            'birth_date': CustomUser(),
            'date_joined': forms.TextInput(),
            'last_login': forms.TextInput(),
        }


class UserPasswordForm(ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ('current_password', 'new_password', 'confirm_password', )