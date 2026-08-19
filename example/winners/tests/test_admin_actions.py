from django.contrib import admin
from django.test import RequestFactory, TestCase

from import_export_celery.admin_actions import create_export_job_action
from import_export_celery.models import ExportJob

from winners.admin import WinnerAdmin
from winners.models import Winner


class CreateExportJobActionTests(TestCase):
    def test_creates_job_with_native_pk_list(self):
        alice = Winner.objects.create(name="Alice")
        bob = Winner.objects.create(name="Bob")
        request = RequestFactory().post("/")
        modeladmin = WinnerAdmin(Winner, admin.site)

        response = create_export_job_action(
            modeladmin, request, Winner.objects.order_by("pk")
        )

        self.assertEqual(response.status_code, 302)
        job = ExportJob.objects.get()
        self.assertEqual(job.queryset, [alice.pk, bob.pk])
        self.assertEqual(
            [alice, bob],
            list(job.get_queryset().order_by("pk")),
        )
