import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from core.models import Assignment, Notification, User, Submission

class Command(BaseCommand):
    help = 'Send assignment reminders to students 2 days, 1 day, and on deadline day'

    def handle(self, *args, **options):
        now = timezone.now()
        # Find assignments whose deadline hasn't fully passed (or is today)
        assignments = Assignment.objects.filter(deadline__date__gte=now.date())
        
        students = User.objects.filter(role='student')
        count = 0
        
        for assignment in assignments:
            days_left = (assignment.deadline.date() - now.date()).days
            
            if days_left in [2, 1, 0]:
                for student in students:
                    # Check if student already submitted
                    if not Submission.objects.filter(assignment=assignment, student=student).exists():
                        day_str = f"{days_left} days" if days_left > 1 else "1 day"
                        if days_left == 0:
                            day_str = "TODAY"
                            
                        msg = f"Reminder: Assignment '{assignment.title}' is due in {day_str}!"
                        
                        # Prevent duplicate identical notifications simply by checking if one exists
                        # (in a real system, you'd track per-assignment-per-day, but this works for demo)
                        if not Notification.objects.filter(user=student, message=msg).exists():
                            Notification.objects.create(user=student, message=msg)
                            self.stdout.write(self.style.SUCCESS(f"Notified {student.username} regarding {assignment.title}"))
                            
                            # Send Email (Printed to console due to EMAIL_BACKEND setting)
                            from django.core.mail import send_mail
                            if student.email:
                                send_mail(
                                    subject=f"AssignMate Reminder: {assignment.title}",
                                    message=msg,
                                    from_email="noreply@assignmate.com",
                                    recipient_list=[student.email],
                                    fail_silently=True
                                )
                            count += 1

        self.stdout.write(self.style.SUCCESS(f"Finished sending {count} reminders."))
