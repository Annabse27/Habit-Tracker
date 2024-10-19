from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Настройки celery загружаются из django.conf:settings с пространством
# имен "CELERY"
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи (tasks.py в каждом приложении)
app.autodiscover_tasks()
