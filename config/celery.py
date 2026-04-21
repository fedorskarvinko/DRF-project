import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создаем экземпляр приложения Celery
app = Celery('LMS_System')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим и регистрируем задачи в приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'deactivate-inactive-users': {
        'task': 'users.tasks.deactivate_inactive_users',
        'schedule': crontab(minute=0, hour=3),  # Каждый день в 3:00
        'options': {
            'expires': 3600,
        },
    },
}