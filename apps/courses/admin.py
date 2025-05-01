from django.contrib import admin
from apps.courses.models import Course, Enrollment

# Register your models here.
admin.site.register(Course)
admin.site.register(Enrollment)

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'role', 'student_id')
#     list_filter = ('role',)