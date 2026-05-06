from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Assignment, Submission, Mark, Notification

class CustomUserAdmin(UserAdmin):
    # Add our custom 'role' field to the admin panel
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Roles', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Mark)
admin.site.register(Notification)
