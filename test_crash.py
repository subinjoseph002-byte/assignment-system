import os
import sys

# Add project root to sys.path
sys.path.append(r"c:\Users\subin\OneDrive\Desktop\mca\AWT\Assignment Submission Remainder System")

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assignment_system.settings')
django.setup()

from django.test import Client
from core.models import User
import traceback

client = Client()

for role in ['admin', 'teacher', 'student']:
    User.objects.filter(username=f'test_{role}').delete()
    User.objects.create_user(username=f'test_{role}', password='123', role=role)
    
    print(f"\n--- Testing {role.upper()} ---")
    client.post('/login/', {'username': f'test_{role}', 'password': '123'})
    try:
        resp = client.get('/dashboard/', follow=True)
        print(f"[{role}] Dashboard status: {resp.status_code}")
    except Exception as e:
        print(f"[{role}] CRASH TRACEBACK:")
        traceback.print_exc()
    client.logout()
