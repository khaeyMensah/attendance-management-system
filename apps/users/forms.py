from django import forms
from apps.users.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    pass


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput())
    full_name = forms.CharField(max_length=50, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "role", "password1", "password2")
