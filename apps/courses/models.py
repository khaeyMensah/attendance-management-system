from django.db import models
from django.core.exceptions import ValidationError
from apps.users.models import User

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role':'lecturer'}, related_name='courses_taught')
    # created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.lecturer_id and self.lecturer.role != 'lecturer':
            raise ValidationError({'lecturer': 'Selected user must have lecturer role.'})
    
    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'course'], name='courses_unique_enrollment'),
        ]
        indexes = [
            models.Index(fields=['course', 'student']),
        ]

    def clean(self):
        if self.student_id and self.student.role != 'student':
            raise ValidationError({'student': 'Selected user must have student role.'})
        
    def __str__(self):
        return f"{self.student} - {self.course}"
