from django.db import models
from django.contrib.auth.models import AbstractUser



'''
-------------------------------
USER MODEL — Role-Based Access
-------------------------------
This model supports three user roles:
  1. 'student'  → Regular student users who check attendance.
  2. 'lecturer' → Faculty users who create courses and generate QR sessions.
  3. 'admin'    → Staff with elevated privileges.  
  

Notes:
- Only one of `student_id` or `staff_id` is required depending on role.
- Admin users will use Django's default admin interface (no custom views for now).
- This setup allows for role-based expansion (e.g., dashboards, permissions) in future.
- Role logic can be handled in views using simple role checks or decorators.
'''


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student','Student'),
        ('lecturer','Lecturer'),
        ('admin','Admin'),
    )
    
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    # Student-specific fields
    student_id = models.CharField(max_length=10, unique=True, null=True, blank=True, help_text="Student's unique index number")
    
    # Lecturer-specific fields
    staff_id = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="Lecturer's staff identification number") 
    
    # Common fields
    email = models.EmailField(max_length=50, unique=True, help_text="User's email address")
    full_name = models.CharField(max_length=50, help_text="User's full name")
    
    def is_student(self):
        return self.role == 'student'
    
    def is_lecturer(self):
        return self.role == 'lecturer'
    
    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return f"{self.full_name} ({self.role})"