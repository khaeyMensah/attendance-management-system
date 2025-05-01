from django.contrib import admin
from apps.attendance.models import AttendanceRecord, Enrollment, Session

# Register your models here.
admin.site.register(Session)
admin.site.register(Enrollment)
admin.site.register(AttendanceRecord)
