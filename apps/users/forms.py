from django import forms
from apps.users.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    
    class Meta:
        model = User
        # fields = ("email", "password",)
    

class RegisterForm(UserCreationForm):
    forms.EmailField(max_length=254, required=True, widget=forms.EmailInput())
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    