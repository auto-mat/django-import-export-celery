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

from author.decorators import with_author

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from import_export.formats.base_formats import DEFAULT_FORMATS

from ..tasks import run_import_job

@with_author
class ImportJob(models.Model):
    file = models.FileField(
        verbose_name=_("File to be imported"),
        upload_to='django-import-export-celery-import-jobs',
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

    imported = models.DateTimeField(
        verbose_name=_("Has the import been completed? If so when?"),
        null=True,
        blank=True,
        default=None,
    )

    format = models.CharField(
        verbose_name=_("Format of file to be imported"),
        max_length=40,
        choices=[(f.CONTENT_TYPE, f.CONTENT_TYPE) for f in DEFAULT_FORMATS],
        # TODO only include formats that pass the tests in import_export get_import_formats
        # https://github.com/django-import-export/django-import-export/blob/master/import_export/admin.py#L121
    )

    change_summary = models.FileField(
        verbose_name=_("Summary of changes made by this import"),
        upload_to='django-import-export-celery-import-change-summaries',
        blank=True,
        null=True,
    )

    errors = models.TextField(
        default='',
        blank=True,
    )

    model = models.CharField(
        verbose_name=_("Name of model to import to"),
        max_length=160,
        choices=[(x,x) for x in getattr(settings, 'IMPORT_EXPORT_CELERY_MODELS', {}).keys()],
    )


@receiver(post_save, sender=ImportJob)
def importjob_post_save(sender, instance, **kwargs):
    if not instance.processing_initiated:
        instance.processing_initiated = datetime.now()
        instance.save()
        run_import_job.delay(instance.pk, dry_run=True)
