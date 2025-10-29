# audio_analysis/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audio_analysis.settings')

# Create the Celery app
app = Celery('audio_analysis')

# Load custom config from settings.py using the 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')
   
# Auto-discover tasks from installed apps
app.autodiscover_tasks()

