"""
Настройка Celery для проекта
"""
import os

from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eigth_module.settings')

# Создаем экземпляр Celery
app = Celery('eigth_module')

# Загружаем настройки из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях Django
app.autodiscover_tasks()

# Настройка расписания для celery-beat
app.conf.beat_schedule = {
    'block-inactive-users': {
        'task': 'users.tasks.block_inactive_users',
        'schedule': crontab(hour=0, minute=0),  # Каждый день в полночь
    },
}

app.conf.timezone = 'UTC'

