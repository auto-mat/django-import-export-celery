# Copyright (C) 2019 o.s. Auto*Mat
from django.utils import timezone
import json

from author.decorators import with_author

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db import transaction
from django.dispatch import receiver

from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from ..fields import ImportExportFileField
from ..tasks import run_export_job
from ..utils import get_formats


@with_author
class ExportJob(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._content_type = None

    file = ImportExportFileField(
        verbose_name=_("exported file"),
        upload_to="django-import-export-celery-export-jobs",
        blank=False,
        null=False,
        max_length=255,
    )

    processing_initiated = models.DateTimeField(
        verbose_name=_("Have we started processing the file? If so when?"),
        null=True,
        blank=True,
        default=None,
    )

    job_status = models.CharField(
        verbose_name=_("Status of the job"),
        max_length=160,
        blank=True,
    )

    format = models.CharField(
        verbose_name=_("Format of file to be exported"),
        max_length=255,
        blank=False,
        null=True,
    )

    app_label = models.CharField(
        verbose_name=_("App label of model to export from"),
        max_length=160,
    )

    model = models.CharField(
        verbose_name=_("Name of model to export from"),
        max_length=160,
    )

    resource = models.CharField(
        verbose_name=_("Resource to use when exporting"),
        max_length=255,
        default="",
    )

    queryset = models.TextField(
        verbose_name=_("JSON list of pks to export"),
        null=False,
    )

    email_on_completion = models.BooleanField(
        verbose_name=_("Send me an email when this export job is complete"),
        default=True,
    )

    site_of_origin = models.TextField(
        verbose_name=_("Site of origin"),
        max_length=255,
        default="",
    )

    class Meta:
        verbose_name = _("Export job")
        verbose_name_plural = _("Export jobs")

    def get_resource_class(self):
        if self.resource:
            return (
                self.get_content_type()
                .model_class()
                .export_resource_classes()[self.resource][1]
            )

    def get_content_type(self):
        if not self._content_type:
            self._content_type = ContentType.objects.get(
                app_label=self.app_label,
                model=self.model,
            )
        return self._content_type

    def get_queryset(self):
        pks = json.loads(self.queryset)
        # If customised queryset for the model exists
        # then it'll apply filter on that otherwise it'll
        # apply filter directly on the model.
        resource_class = self.get_resource_class()
        if hasattr(resource_class, "get_export_queryset"):
            return resource_class().get_export_queryset().filter(pk__in=pks)
        return self.get_content_type().model_class().objects.filter(pk__in=pks)

    def get_resource_choices(self):
        return [
            (k, v[0])
            for k, v in self.get_content_type()
            .model_class()
            .export_resource_classes()
            .items()
        ]

    @staticmethod
    def get_format_choices():
        """returns choices of available export formats"""
        return [
            (f.CONTENT_TYPE, f().get_title())
            for f in get_formats()
            if f().can_export()
        ]


@receiver(post_save, sender=ExportJob)
def exportjob_post_save(sender, instance, **kwargs):
    if instance.resource and not instance.processing_initiated:
        instance.processing_initiated = timezone.now()
        instance.save()
        transaction.on_commit(lambda: run_export_job.delay(instance.pk))
