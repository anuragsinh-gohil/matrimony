from django.contrib import admin
from .models import Profile, Event, Reminder

admin.site.register(Profile)
admin.site.register(Event)
admin.site.register(Reminder)