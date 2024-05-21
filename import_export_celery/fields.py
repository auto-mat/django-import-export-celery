from django.conf import settings
from django.core.files.storage import storages
from django.db import models


def lazy_initialize_storage_class():
    # If the user has specified a custom storage backend, use it.
    if getattr(settings, "IMPORT_EXPORT_CELERY_STORAGE", None):
        try:
            from django.core.files.storage import get_storage_class
            storage_class = get_storage_class(settings.IMPORT_EXPORT_CELERY_STORAGE)
            return storage_class()
        except (ImportError, TypeError):
            return storages[settings.IMPORT_EXPORT_CELERY_STORAGE]

    return None


class ImportExportFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        kwargs["storage"] = lazy_initialize_storage_class
        super().__init__(*args, **kwargs)
