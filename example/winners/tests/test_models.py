import os
from django.test import TestCase
from django.core.files.base import ContentFile

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
