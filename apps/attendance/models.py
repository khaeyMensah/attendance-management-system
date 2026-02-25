from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.courses.models import Course
from apps.courses.models import Enrollment
from apps.users.models import User

class Session(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(help_text="QR code expiration time")
    qr_token = models.CharField(max_length=50, unique=True, db_index=True)
    access_code = models.CharField(max_length=8, unique=True, db_index=True, help_text="Short code alternative to QR scan")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                name='attendance_session_end_after_start',
                condition=models.Q(end_time__gt=models.F('start_time')),
            ),
        ]
        indexes = [
            models.Index(fields=['course', 'start_time']),
            models.Index(fields=['course', 'is_active']),
        ]
        
    def __str__(self):
        return f"{self.course.code} @ {self.start_time.strftime('%H:%M')}"

    def clean(self):
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'End time must be later than start time.'})

    def is_open(self, at_time=None):
        current_time = at_time or timezone.now()
        return self.is_active and self.start_time <= current_time <= self.end_time
    
class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('invalid', 'Invalid'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role':'student'}, related_name='attendance_records')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendance_records')
    check_in_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'session'], name='attendance_unique_student_session'),
        ]
        indexes = [
            models.Index(fields=['student', 'session']),
        ]
        
    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"

    def clean(self):
        if self.student_id and self.student.role != 'student':
            raise ValidationError({'student': 'Selected user must have student role.'})

        if self.student_id and self.session_id:
            is_enrolled = Enrollment.objects.filter(
                student_id=self.student_id,
                course_id=self.session.course_id,
            ).exists()
            if not is_enrolled:
                raise ValidationError({'student': 'Student is not enrolled in this course.'})

            if self.status == 'present' and not self.session.is_open():
                raise ValidationError({'session': 'Attendance can only be logged while session is active.'})
    
    
