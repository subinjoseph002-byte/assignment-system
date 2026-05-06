from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    marking_criteria = models.TextField(blank=True, null=True, help_text="Specify the criteria for grading this assignment.")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_created')
    created_at = models.DateTimeField(auto_now_add=True)

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.deadline

class Mark(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='mark')
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField(blank=True, null=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
