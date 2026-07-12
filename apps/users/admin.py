from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('ClassMark profile', {'fields': ('full_name', 'role', 'student_id', 'staff_id')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('ClassMark profile', {'fields': ('full_name', 'email', 'role', 'student_id', 'staff_id')}),
    )
    list_display = (
        'username',
        'full_name',
        'email',
        'role',
        'student_id',
        'staff_id',
        'is_active',
        'is_staff',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'full_name', 'email', 'student_id', 'staff_id')
    ordering = ('role', 'username')
