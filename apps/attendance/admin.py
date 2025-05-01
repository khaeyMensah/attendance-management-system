from django.contrib import admin
from apps.attendance.models import AttendanceRecord, Session

# Register your models here.
admin.site.register(Session)
admin.site.register(AttendanceRecord)
