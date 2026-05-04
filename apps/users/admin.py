from django.contrib import admin
from apps.users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'role', 'student_id', 'staff_id', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'full_name', 'email', 'student_id', 'staff_id')
