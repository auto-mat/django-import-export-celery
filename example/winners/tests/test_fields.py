import django
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import unittest

from import_export_celery.fields import lazy_initialize_storage_class


class FooTestingStorage(FileSystemStorage):
    pass


class InitializeStorageClassTests(TestCase):

    def test_default(self):
        self.assertIsInstance(lazy_initialize_storage_class(), FileSystemStorage)

    @unittest.skipUnless(django.VERSION < (5, 1), "Test only applicable for Django versions < 5.1")
    @override_settings(
        IMPORT_EXPORT_CELERY_STORAGE="winners.tests.test_fields.FooTestingStorage"
    )
    def test_old_style(self):
        del settings.IMPORT_EXPORT_CELERY_STORAGE_ALIAS
        del settings.STORAGES
        self.assertIsInstance(lazy_initialize_storage_class(), FooTestingStorage)

    @unittest.skipUnless((4, 2) <= django.VERSION, "Test only applicable for Django 4.2 and later")
    @override_settings(
        IMPORT_EXPORT_CELERY_STORAGE_ALIAS="test_import_export_celery",
        STORAGES={
            "test_import_export_celery": {
                "BACKEND": "winners.tests.test_fields.FooTestingStorage",
            },
            "staticfiles": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
            },
            "default": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
            }
        }

    )
    def test_new_style(self):
        self.assertIsInstance(lazy_initialize_storage_class(), FooTestingStorage)

    @unittest.skipUnless((4, 2) <= django.VERSION, "Test only applicable for Django 4.2 and later")
    @override_settings(
        STORAGES={
            "staticfiles": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
            },
            "default": {
                "BACKEND": "winners.tests.test_fields.FooTestingStorage",
            }
        }
    )
    def test_default_storage(self):
        """ Test that "default" storage is used when no alias is provided """
        self.assertIsInstance(lazy_initialize_storage_class(), FooTestingStorage)
