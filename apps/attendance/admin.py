from django.contrib import admin
from apps.attendance.models import AttendanceRecord, Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('course', 'start_time', 'end_time', 'access_code', 'is_active')
    list_filter = ('is_active', 'course')
    search_fields = ('course__code', 'course__title', 'access_code', 'qr_token')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'check_in_time')
    list_filter = ('status', 'session__course')
    search_fields = ('student__username', 'student__full_name', 'session__course__code')
