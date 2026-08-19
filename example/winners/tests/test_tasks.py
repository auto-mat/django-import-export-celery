from django.test import TestCase

from import_export_celery.models import ExportJob
from import_export_celery.tasks import run_export_job

from winners.models import Winner


class ExportJobTestBase(TestCase):
    def setUp(self):
        self.alice = Winner.objects.create(name="Alice")
        self.bob = Winner.objects.create(name="Bob")

    def _create_job(self, resource, resource_kwargs=None, queryset_spec=None):
        job = ExportJob.objects.create(
            app_label="winners",
            model="winner",
            queryset=(
                queryset_spec
                if queryset_spec is not None
                else [self.alice.pk, self.bob.pk]
            ),
            site_of_origin="http://testserver",
            email_on_completion=False,
            **({"resource_kwargs": resource_kwargs} if resource_kwargs is not None else {}),
        )
        # Set resource/format via update() to sidestep the post_save signal,
        # which would try to queue a real celery task.
        ExportJob.objects.filter(pk=job.pk).update(
            resource=resource, format="text/csv"
        )
        job.refresh_from_db()
        return job

    def _exported_content(self, job):
        run_export_job(job.pk)
        job.refresh_from_db()
        with job.file.open("r") as f:
            content = f.read()
        return content.decode("utf8") if isinstance(content, bytes) else content


class RunExportJobResourceKwargsTests(ExportJobTestBase):
    """resource_kwargs must reach the resource constructor both when the
    queryset is built (ExportJob.get_queryset) and when the export itself
    runs (tasks.run_export_job)."""

    def test_default_is_empty_dict(self):
        job = self._create_job("winners")
        self.assertEqual(job.resource_kwargs, {})

    def test_export_without_kwargs_still_works(self):
        content = self._exported_content(self._create_job("winners"))
        self.assertIn("Alice", content)
        self.assertIn("Bob", content)

    def test_kwargs_reach_resource_constructor_during_export(self):
        content = self._exported_content(
            self._create_job("winners_parameterized", {"prefix": "prized "})
        )
        self.assertIn("prized Alice", content)
        self.assertIn("prized Bob", content)

    def test_kwargs_scope_the_export_queryset(self):
        job = self._create_job(
            "winners_parameterized", {"name_contains": "Ali"}
        )
        self.assertEqual([self.alice], list(job.get_queryset()))
        content = self._exported_content(job)
        self.assertIn("Alice", content)
        self.assertNotIn("Bob", content)


class ExportJobQuerysetFiltersTests(ExportJobTestBase):
    """A dict in ExportJob.queryset is a set of queryset filters, evaluated
    when the job runs (unlike a pk list, which is fixed at creation)."""

    def test_dict_filters_are_evaluated_at_run_time(self):
        job = self._create_job("winners", queryset_spec={"name__startswith": "A"})
        anna = Winner.objects.create(name="Anna")  # created AFTER the job
        content = self._exported_content(job)
        self.assertIn("Alice", content)
        self.assertIn("Anna", content)
        self.assertNotIn("Bob", content)
        self.assertIn(anna, job.get_queryset())

    def test_empty_dict_exports_everything(self):
        content = self._exported_content(
            self._create_job("winners", queryset_spec={})
        )
        self.assertIn("Alice", content)
        self.assertIn("Bob", content)

    def test_empty_list_exports_nothing(self):
        content = self._exported_content(
            self._create_job("winners", queryset_spec=[])
        )
        self.assertNotIn("Alice", content)
        self.assertNotIn("Bob", content)

    def test_invalid_spec_raises(self):
        job = self._create_job("winners", queryset_spec="not-a-spec")
        with self.assertRaisesMessage(ValueError, "'not-a-spec'"):
            job.get_queryset()

    def test_filters_compose_with_resource_kwargs(self):
        content = self._exported_content(
            self._create_job(
                "winners_parameterized",
                resource_kwargs={"prefix": "prized "},
                queryset_spec={"name__startswith": "A"},
            )
        )
        self.assertIn("prized Alice", content)
        self.assertNotIn("Bob", content)
