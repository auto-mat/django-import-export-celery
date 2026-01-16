import os
from django.test import TestCase, override_settings
from django.core.files.base import ContentFile

from import_export_celery.models.exportjob import ExportJob
from import_export_celery.models.importjob import ImportJob


class ImportJobTestCases(TestCase):

    def test_delete_file_on_job_delete(self):
        job = ImportJob.objects.create(
            file=ContentFile(b"", "file.csv"),
        )
        file_path = job.file.path
        assert os.path.exists(file_path)
        job.delete()
        assert not os.path.exists(file_path)
        assert not ImportJob.objects.filter(id=job.id).exists()


class ExportJobTestCases(TestCase):
    def test_create_export_job_default_email_on_completion(self):
        job = ExportJob.objects.create(
            app_label="winners", model="Winner"
        )
        job.refresh_from_db()
        self.assertTrue(job.email_on_completion)

    @override_settings(EXPORT_JOB_EMAIL_ON_COMPLETION=False)
    def test_create_export_job_false_email_on_completion(self):
        job = ExportJob.objects.create(
            app_label="winners", model="Winner"
        )
        job.refresh_from_db()
        self.assertFalse(job.email_on_completion)
