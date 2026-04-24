import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blood_bank_project.settings')
django.setup()

from blood_bank.models import BloodStock

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

for bg in BLOOD_GROUPS:
    BloodStock.objects.get_or_create(blood_group=bg)

print("Blood stock initialized.")
