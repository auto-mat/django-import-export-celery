# -*- coding: utf-8 -*-
# Author: Timothy Hobbs <timothy <at> hobbs.cz>
from datetime import datetime
import os

from celery import shared_task

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.core.mail import send_mail

from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

from import_export.formats.base_formats import DEFAULT_FORMATS

from . import models
from .model_config import ModelConfig

from celery.utils.log import get_task_logger
import logging

logger = logging.getLogger(__name__)

log = get_task_logger(__name__)


importables = getattr(settings, "IMPORT_EXPORT_CELERY_MODELS", {})


def change_job_status(job, direction, job_status, dry_run=False):
    if dry_run:
        job_status = "[Dry run] " + job_status
    else:
        job_status = job_status
    cache.set(direction + "_job_status_%s" % job.pk, job_status)
    job.job_status = job_status
    job.save()


def get_format(job):
    for format in DEFAULT_FORMATS:
        if job.format == format.CONTENT_TYPE:
            return format()
            break


def _run_import_job(import_job, dry_run=True):
    change_job_status(import_job, "import", "1/5 Import started", dry_run)
    if dry_run:
        import_job.errors = ""
    model_config = ModelConfig(**importables[import_job.model])
    import_format = get_format(import_job)
    try:  # Copied from https://github.com/django-import-export/django-import-export/blob/3c082f98afe7996e79f936418fced3094f141c26/import_export/admin.py#L260 sorry
        data = import_job.file.read()
        if not import_format.is_binary():
            data = force_text(data, "utf8")
        dataset = import_format.create_dataset(data)
    except UnicodeDecodeError as e:
        import_job.errors += _("Imported file has a wrong encoding: %s" % e) + "\n"
        change_job_status(
            import_job, "import", "Imported file has a wrong encoding", dry_run
        )
        import_job.save()
        return
    except Exception as e:
        import_job.errors += _("Error reading file: %s") % e + "\n"
        change_job_status(import_job, "import", "Error reading file", dry_run)
        import_job.save()
        return
    change_job_status(import_job, "import", "2/5 Processing import data", dry_run)

    class Resource(model_config.resource):
        def before_import_row(self, row, **kwargs):
            if "row_number" in kwargs:
                row_number = kwargs["row_number"]
                if row_number % 100 == 0 or row_number == 1:
                    change_job_status(
                        import_job,
                        "import",
                        "3/5 Importing row %s/%s" % (row_number, len(dataset)),
                        dry_run,
                    )
            return super(Resource, self).before_import_row(row, **kwargs)

    resource = Resource()

    result = resource.import_data(dataset, dry_run=dry_run)
    change_job_status(import_job, "import", "4/5 Generating import summary", dry_run)
    for error in result.base_errors:
        import_job.errors += "\n%s\n%s\n" % (error.error, error.traceback)
    for line, errors in result.row_errors():
        for error in errors:
            import_job.errors += _("Line: %s - %s\n\t%s\n%s") % (
                line,
                error.error,
                ",".join(str(s) for s in error.row.values()),
                error.traceback,
            )

    if dry_run:
        summary = "<html>"
        summary += "<head>"
        summary += '<meta charset="utf-8">'
        summary += "</head>"
        summary += "<body>"
        summary += '<table  border="1">'  # TODO refactor the existing template so we can use it for this
        # https://github.com/django-import-export/django-import-export/blob/6575c3e1d89725701e918696fbc531aeb192a6f7/import_export/templates/admin/import_export/import.html
        if not result.invalid_rows:
            cols = lambda row: "</td><td>".join([field for field in row.diff])
            summary += (
                "<tr><td>change_type</td><td>"
                + "</td><td>".join(
                    [f.column_name for f in resource.get_user_visible_fields()]
                )
                + "</td></tr>"
            )
            summary += (
                "<tr><td>"
                + "</td></tr><tr><td>".join(
                    [
                        row.import_type + "</td><td>" + cols(row)
                        for row in result.valid_rows()
                    ]
                )
                + "</tr>"
            )
        else:
            cols = lambda row: "</td><td>".join([str(field) for field in row.values])
            cols_error = lambda row: "".join(
                [
                    "<mark>"
                    + key
                    + "</mark>"
                    + "<br>"
                    + row.error.message_dict[key][0]
                    + "<br>"
                    for key in row.error.message_dict.keys()
                ]
            )
            summary += (
                "<tr><td>row</td>"
                + "<td>errors</td><td>"
                + "</td><td>".join(
                    [f.column_name for f in resource.get_user_visible_fields()]
                )
                + "</td></tr>"
            )
            summary += (
                "<tr><td>"
                + "</td><td></td></tr><tr><td>".join(
                    [
                        str(row.number)
                        + "</td><td>"
                        + cols_error(row)
                        + "</td><td>"
                        + cols(row)
                        for row in result.invalid_rows
                    ]
                )
                + "</tr>"
            )
        summary += "</table>"
        summary += "</body>"
        summary += "</html>"
        import_job.change_summary.save(
            os.path.split(import_job.file.name)[1] + ".html",
            ContentFile(summary.encode("utf-8")),
        )
    else:
        import_job.imported = datetime.now()
    change_job_status(import_job, "import", "5/5 Import job finished", dry_run)
    import_job.save()


@shared_task(bind=False)
def run_import_job(pk, dry_run=True):
    log.info("Importing %s dry-run %s" % (pk, dry_run))
    import_job = models.ImportJob.objects.get(pk=pk)
    try:
        _run_import_job(import_job, dry_run)
    except Exception as e:
        import_job.errors += _("Import error %s") % e + "\n"
        change_job_status(import_job, "import", "Import error", dry_run)
        import_job.save()
        return


@shared_task(bind=False)
def run_export_job(pk):
    log.info("Exporting %s" % pk)
    export_job = models.ExportJob.objects.get(pk=pk)
    resource_class = export_job.get_resource_class()
    queryset = export_job.get_queryset()
    qs_len = len(queryset)

    class Resource(resource_class):
        def __init__(self, *args, **kwargs):
            self.row_number = 1
            super().__init__(*args, **kwargs)

        def export_resource(self, *args, **kwargs):
            if self.row_number % 20 == 0 or self.row_number == 1:
                change_job_status(
                    export_job,
                    "export",
                    "Exporting row %s/%s" % (self.row_number, qs_len),
                )
            self.row_number += 1
            return super(Resource, self).export_resource(*args, **kwargs)

    resource = Resource()

    data = resource.export(queryset)
    format = get_format(export_job)
    serialized = format.export_data(data)
    change_job_status(export_job, "export", "Export complete")
    filename = "{app}-{model}-{date}.{extension}".format(
        app=export_job.app_label,
        model=export_job.model,
        date=str(datetime.now()),
        extension=format.get_extension(),
    )
    if not format.is_binary():
        serialized = serialized.encode("utf8")
    export_job.file.save(filename, ContentFile(serialized))
    if export_job.email_on_completion:
        send_mail(
            _("Django: Export job completed"),
            _(
                "Your export job on model {app_label}.{model} has completed. You can download the file at the following link:\n\n{link}"
            ).format(
                app_label=export_job.app_label,
                model=export_job.model,
                link=export_job.site_of_origin
                + reverse(
                    "admin:%s_%s_change"
                    % (export_job._meta.app_label, export_job._meta.model_name,),
                    args=[export_job.pk],
                ),
            ),
            settings.SERVER_EMAIL,
            [export_job.updated_by.email],
        )
    return
