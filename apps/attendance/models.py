from django.db import models
from apps.courses.models import Course
from apps.users.models import User

class Session(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(help_text="QR code expiration time")
    qr_token = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['qr_token'])
        ]
        
    def __str__(self):
        return f"{self.course.code} @ {self.start_time.strftime('%H:%M')}"
    
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'course')
        
    def __str__(self):
        return f"{self.student} - {self.course}"
    
    
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
        unique_together = [['student', 'session']]
        indexes = [
            models.Index(fields=['student', 'session']),
        ]
        
    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"
    
    