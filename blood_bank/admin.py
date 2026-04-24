from django.contrib import admin
from .models import Profile, BloodStock, BloodRequest

admin.site.register(Profile)
admin.site.register(BloodStock)
admin.site.register(BloodRequest)
