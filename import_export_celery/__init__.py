from django.conf import settings
import importlib
celery_module = getattr(settings, 'IMPORT_EXPORT_CELERY_INIT_MODULE', 'project.celery')
celery_app = importlib.import_module(celery_module).app
