from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignUpForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name' , 'last_name', 'email', 'password', 'phone_number', 'gender', 'province', 'district', 'tole','image']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(label='Password',widget=forms.PasswordInput)


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label='Search')