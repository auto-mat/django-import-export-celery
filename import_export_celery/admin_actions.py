from django.utils import timezone
import json
from uuid import UUID

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.shortcuts import redirect

from .models import ExportJob
from .utils import get_formats
from . import tasks


def run_import_job_action(modeladmin, request, queryset):
    for instance in queryset:
        tasks.logger.info("Importing %s dry-run: False" % (instance.pk))
        tasks.run_import_job.delay(instance.pk, dry_run=False)


run_import_job_action.short_description = _("Perform import")


def run_import_job_action_dry(modeladmin, request, queryset):
    for instance in queryset:
        tasks.logger.info("Importing %s dry-run: True" % (instance.pk))
        tasks.run_import_job.delay(instance.pk, dry_run=True)


run_import_job_action_dry.short_description = _("Perform dry import")


def run_export_job_action(modeladmin, request, queryset):
    for instance in queryset:
        instance.processing_initiated = timezone.now()
        instance.save()
        tasks.run_export_job.delay(instance.pk)


run_export_job_action.short_description = _("Run export job")


def create_export_job_action(modeladmin, request, queryset):
    if queryset:
        arbitrary_obj = queryset.first()
        ej = ExportJob.objects.create(
            app_label=arbitrary_obj._meta.app_label,
            model=arbitrary_obj._meta.model_name,
            queryset=json.dumps(
                [
                    str(obj.pk) if isinstance(obj.pk, UUID) else obj.pk
                    for obj in queryset
                ]
            ),
            site_of_origin=request.scheme + "://" + request.get_host(),
        )

        #  Load the ExportJob if only one Resource
        resource_choices = ej.get_resource_choices()
        format_choices = get_formats()
        if len(resource_choices) == 1 and len(format_choices) == 1:
            ej.resource = resource_choices[0][0]
            ej.format = format_choices[0].CONTENT_TYPE
            ej.save()

    rurl = reverse(
        "admin:%s_%s_change"
        % (
            ej._meta.app_label,
            ej._meta.model_name,
        ),
        args=[ej.pk],
    )
    return redirect(rurl)


create_export_job_action.short_description = _("Export with celery")
