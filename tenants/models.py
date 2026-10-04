from django.db import models

# Create your models here.
# audit/admin.py
from django.contrib import admin

from audit.models import InferenceRecord, Tenant

admin.site.register(Tenant)
admin.site.register(InferenceRecord)