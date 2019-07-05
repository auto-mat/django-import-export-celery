# -*- coding: utf-8 -*-
# Author: Timothy Hobbs <timothy <at> hobbs.cz>
from datetime import datetime
import os

from celery import task

from django.conf import settings
from django.core.files.base import ContentFile

from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

from import_export.formats.base_formats import DEFAULT_FORMATS

from . import models
from .model_config import ModelConfig


importables = getattr(settings, 'IMPORT_EXPORT_CELERY_MODELS', {})


@task(bind=False)
def run_import_job(pk, dry_run=True):
    while True:
        try:
            import_job = models.ImportJob.objects.get(pk=pk)
            break
        except models.ImportJob.DoesNotExist:
            pass
    model_config = ModelConfig(**importables[import_job.model])

    for format in DEFAULT_FORMATS:
        if import_job.format == format.CONTENT_TYPE:
            input_format = format()
            break
    try:  # Copied from https://github.com/django-import-export/django-import-export/blob/3c082f98afe7996e79f936418fced3094f141c26/import_export/admin.py#L260 sorry
        data = import_job.file.read()
        if not input_format.is_binary():
            data = force_text(data, 'utf8')
        dataset = input_format.create_dataset(data)
    except UnicodeDecodeError as e:
        import_job.errors += _("Imported file has a wrong encoding: %s" % e) + "\n"
        import_job.save()
        return
    except Exception as e:
        import_job.errors += _("Error reading file: %s" % e) + "\n"
        import_job.save()
        return
    resource = model_config.resource()
    result = resource.import_data(dataset, dry_run=dry_run)
    if dry_run:
        summary = '<table  border="1">' # TODO refactor the existing template so we can use it for this
        # https://github.com/django-import-export/django-import-export/blob/6575c3e1d89725701e918696fbc531aeb192a6f7/import_export/templates/admin/import_export/import.html
        summary += '<tr><td>change_type</td><td>' + '</td><td>'.join([f.column_name for f in resource.get_user_visible_fields()]) + '</td></tr>'
        cols = lambda row: '</td><td>'.join([field for field in row.diff])
        summary += '<tr><td>' + '</td></tr><tr><td>'.join([row.import_type + '</td><td>' + cols(row) for row in result.valid_rows()]) + '</tr>'
        summary += '</table>'
        import_job.change_summary.save(os.path.split(import_job.file.name)[1]+".html", ContentFile(summary))
    else:
        import_job.imported =  datetime.now()
    import_job.save()

def run_import_job_action(modeladmin, request, queryset):
    for instance in queryset:
        run_import_job.delay(instance.pk, dry_run=False)

run_import_job_action.short_description = _("Perform import")
