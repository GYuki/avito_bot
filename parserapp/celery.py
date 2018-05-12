from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from parserbot import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parserbot.settings')
app = Celery('avito')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
