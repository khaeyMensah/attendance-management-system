from django.db import models
from apps.users.models import User

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role':'lecturer'}, related_name='courses_taught')
    # created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.title}"
