from django import forms

from apps.courses.models import Enrollment
from apps.users.models import User


class CourseEnrollmentForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select students to enroll in this course.',
    )

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        enrolled_student_ids = Enrollment.objects.filter(course=course).values_list(
            'student_id',
            flat=True,
        )
        self.fields['students'].queryset = User.objects.filter(
            role='student',
            is_active=True,
        ).exclude(
            id__in=enrolled_student_ids,
        ).order_by('full_name', 'username')
