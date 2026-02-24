from django import forms
from apps.users.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput())
    full_name = forms.CharField(max_length=50, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    identification = forms.CharField(max_length=64, required=False, help_text='Student or staff ID if required by your role')

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "role", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            ('student', 'Student'),
            ('lecturer', 'Lecturer'),
        ]

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        identification = (cleaned.get('identification') or '').strip()

        # Require identification for student and lecturer roles
        if role in ('student', 'lecturer') and not identification:
            raise forms.ValidationError('An ID is required for the selected role.')

        if role == 'student' and identification and len(identification) > 10:
            self.add_error('identification', 'Student ID cannot exceed 10 characters.')
        if role == 'lecturer' and identification and len(identification) > 20:
            self.add_error('identification', 'Staff ID cannot exceed 20 characters.')

        # Ensure identification is unique for the appropriate model field
        if identification:
            if role == 'student':
                if User.objects.filter(student_id=identification).exists():
                    raise forms.ValidationError('This student ID is already registered.')
            if role == 'lecturer':
                if User.objects.filter(staff_id=identification).exists():
                    raise forms.ValidationError('This staff ID is already registered.')

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        # set role if model supports it
        role = self.cleaned_data.get('role')
        if role and hasattr(user, 'role'):
            setattr(user, 'role', role)

        ident = (self.cleaned_data.get('identification') or '').strip()
        if hasattr(user, 'student_id'):
            user.student_id = None
        if hasattr(user, 'staff_id'):
            user.staff_id = None
        if ident:
            if role == 'student' and hasattr(user, 'student_id'):
                user.student_id = ident
            elif role == 'lecturer' and hasattr(user, 'staff_id'):
                user.staff_id = ident

        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    pass


class ProfileForm(forms.ModelForm):
    pass
