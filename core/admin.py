from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Assignment, Submission, Mark, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    # Add our custom 'role' field to the admin panel views
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'teacher', 'deadline']
    list_filter = ['subject', 'teacher', 'deadline']
    search_fields = ['title', 'description', 'subject']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at', 'is_late']
    list_filter = ['assignment', 'student', 'submitted_at']

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ['submission', 'marks']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
