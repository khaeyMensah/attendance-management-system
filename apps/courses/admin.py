from django.contrib import admin
from apps.courses.models import Course, Enrollment


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    autocomplete_fields = ('student',)
    fields = ('student', 'enrolled_at')
    readonly_fields = ('enrolled_at',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'lecturer', 'student_count')
    list_filter = ('lecturer',)
    search_fields = ('code', 'title', 'lecturer__username', 'lecturer__full_name')
    autocomplete_fields = ('lecturer',)
    inlines = (EnrollmentInline,)

    @admin.display(description='Students')
    def student_count(self, obj):
        return obj.enrollments.count()


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'course__lecturer')
    search_fields = ('student__username', 'student__full_name', 'student__student_id', 'course__code')
    autocomplete_fields = ('student', 'course')
    readonly_fields = ('enrolled_at',)
