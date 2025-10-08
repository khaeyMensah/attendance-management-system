from django.forms import forms
from users.models import User

class LoginForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ("email", "password",)
    

class RegisterForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ("email", "password",)
    