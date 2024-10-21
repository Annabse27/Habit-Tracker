from celery import Celery

# Создаем экземпляр Celery
app = Celery('proj', broker='redis://redis:6379/0')

# Настраиваем Celery на использование асинхронного воркера gevent
app.conf.update(
    worker_concurrency=1,
    task_always_eager=False,  # Обычные задачи через брокер
    worker_pool='gevent',  # Используем gevent для поддержки асинхронности
)

# Загружаем конфигурацию из файла настроек Django с пространством имен 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи
app.autodiscover_tasks()
