from django.db import models


def lazy_initialize_storage_class():
    from django.conf import settings
    from django.core.files.storage import storages

    if hasattr(settings, "IMPORT_EXPORT_CELERY_STORAGE_ALIAS"):
        # Use the alias configured in STORAGES
        return storages[settings.IMPORT_EXPORT_CELERY_STORAGE_ALIAS]

    # Otherwise, just use the default storage
    return storages["default"]



class ImportExportFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        kwargs["storage"] = lazy_initialize_storage_class
        super().__init__(*args, **kwargs)
