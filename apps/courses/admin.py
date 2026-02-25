from django.contrib import admin
from apps.courses.models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'lecturer')
    list_filter = ('lecturer',)
    search_fields = ('code', 'title', 'lecturer__username', 'lecturer__full_name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course',)
    search_fields = ('student__username', 'student__full_name', 'course__code')
