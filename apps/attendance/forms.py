from django import forms


class StartSessionForm(forms.Form):
    duration_minutes = forms.IntegerField(
        min_value=5,
        max_value=360,
        initial=90,
        help_text='How long the session remains open for attendance.',
    )


class AccessCodeForm(forms.Form):
    access_code = forms.CharField(
        max_length=8,
        min_length=6,
        help_text='Enter the short attendance code from your lecturer.',
    )

    def clean_access_code(self):
        return (self.cleaned_data.get('access_code') or '').strip().upper()
