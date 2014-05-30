from django.contrib import admin

# Register your models here.
from tracker.models import Track, TrackYear

admin.site.register(Track)
admin.site.register(TrackYear)