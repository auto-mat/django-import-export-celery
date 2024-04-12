from django.conf import settings
from django.db import models


def lazy_initialize_storage_class():
    # If the user has specified a custom storage backend, use it.
    if settings.STORAGES.get("IMPORT_EXPORT_CELERY_STORAGE"):
        try:
            # From Django 4.2 and later
            from django.core.files.storage import storages
            from django.core.files.storage.handler import InvalidStorageError
            try:
                storage_class = storages['IMPORT_EXPORT_CELERY_STORAGE']
            except InvalidStorageError:
                from django.utils.module_loading import import_string
                storage_class = settings.DEFAULT_FILE_STORAGE
                storage_class = import_string(storage_class)()
        except ImportError:
            # Deprecated since Django 4.2, Removed in Django 5.1
            from django.core.files.storage import get_storage_class
            storage_class = get_storage_class(
                settings.STORAGES.get("IMPORT_EXPORT_CELERY_STORAGE")["BACKEND"]
            )()
        return storage_class


class ImportExportFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        kwargs["storage"] = lazy_initialize_storage_class
        super().__init__(*args, **kwargs)
