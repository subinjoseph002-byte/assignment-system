import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assignment_system.settings')
django.setup()

from core.models import User

username = os.environ.get('ADMIN_USERNAME', 'admin')
password = os.environ.get('ADMIN_PASSWORD', 'admin123')
email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

user = User.objects.filter(username=username).first()

if not user:
    print(f"Creating superuser {username}...")
    User.objects.create_superuser(username=username, email=email, password=password, role='admin')
    print("Superuser created successfully!")
else:
    print(f"Superuser {username} already exists. Ensuring it has admin role and permissions...")
    user.is_staff = True
    user.is_superuser = True
    user.role = 'admin'
    user.set_password(password) # Update password just in case
    user.save()
    print("Superuser updated.")
