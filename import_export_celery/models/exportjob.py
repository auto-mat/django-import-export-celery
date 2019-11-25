# -*- coding: utf-8 -*-

# Copyright (C) 2019 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
from datetime import datetime
import json

from author.decorators import with_author

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver

from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from import_export.formats.base_formats import DEFAULT_FORMATS

from ..tasks import run_export_job, run_import_job


@with_author
class ExportJob(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._content_type = None

    file = models.FileField(
        verbose_name=_("exported file"),
        upload_to='django-import-export-celery-export-jobs',
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
        choices=[(f.CONTENT_TYPE, f.CONTENT_TYPE) for f in DEFAULT_FORMATS],
        # TODO only include formats that pass the tests in import_export get_export_formats
        # https://github.com/django-import-export/django-import-export/blob/master/import_export/admin.py#L121
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
        default='',
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
        max_length=255,
        default='',
    )

    def get_resource_class(self):
        if self.resource:
            return self.get_content_type().model_class().export_resource_classes()[self.resource][1]

    def get_content_type(self):
        if not self._content_type:
            self._content_type = ContentType.objects.get(
                app_label=self.app_label,
                model=self.model,
            )
        return self._content_type

    def get_queryset(self):
        pks = json.loads(self.queryset)
        return self.get_content_type().model_class().objects.filter(pk__in=pks)

    def get_resource_choices(self):
        return [
            (k, v[0]) for k, v in
            self.get_content_type().model_class().export_resource_classes().items()
        ]



@receiver(post_save, sender=ExportJob)
def exportjob_post_save(sender, instance, **kwargs):
    if instance.resource and not instance.processing_initiated:
        instance.processing_initiated = datetime.now()
        instance.save()
        run_export_job.delay(instance.pk)
