from django.contrib import admin
from apps.courses.models import Course

# Register your models here.
admin.site.register(Course)

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'role', 'student_id')
#     list_filter = ('role',)