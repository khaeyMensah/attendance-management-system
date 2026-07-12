from django.contrib import admin
from apps.attendance.models import AttendanceRecord, Session


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    autocomplete_fields = ('student',)
    readonly_fields = ('check_in_time',)
    fields = ('student', 'status', 'check_in_time')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('course', 'start_time', 'end_time', 'access_code', 'is_active', 'present_count')
    list_filter = ('is_active', 'course', 'course__lecturer')
    search_fields = ('course__code', 'course__title', 'access_code', 'qr_token')
    autocomplete_fields = ('course',)
    inlines = (AttendanceRecordInline,)

    @admin.display(description='Present')
    def present_count(self, obj):
        return obj.attendance_records.filter(status='present').count()


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'check_in_time')
    list_filter = ('status', 'session__course', 'session__course__lecturer')
    search_fields = (
        'student__username',
        'student__full_name',
        'student__student_id',
        'session__course__code',
        'session__access_code',
    )
    autocomplete_fields = ('student', 'session')
    readonly_fields = ('check_in_time',)
