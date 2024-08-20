from django.db import models


def lazy_initialize_storage_class():
    from django.conf import settings
    try:
        from django.core.files.storage import storages
        storages_defined = True
    except ImportError:
        storages_defined = False

    if not hasattr(settings, 'IMPORT_EXPORT_CELERY_STORAGE') and storages_defined:
        # Use new style storages if defined
        storage_alias = getattr(settings, "IMPORT_EXPORT_CELERY_STORAGE_ALIAS", "default")
        storage_class = storages[storage_alias]
    else:
        # Use old style storages if defined
        from django.core.files.storage import get_storage_class
        storage_class = get_storage_class(getattr(settings, "IMPORT_EXPORT_CELERY_STORAGE", "django.core.files.storage.FileSystemStorage"))
        return storage_class()

    return storage_class


class ImportExportFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        kwargs["storage"] = lazy_initialize_storage_class
        super().__init__(*args, **kwargs)
