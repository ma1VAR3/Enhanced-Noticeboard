from django.contrib import admin
# Register your models here.
from .models import Event,FAQ

admin.site.register(Event)
admin.site.register(FAQ)
