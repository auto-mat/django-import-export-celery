from datetime import datetime
import json

from django.utils.translation import ugettext as _
from django.urls import reverse
from django.shortcuts import redirect

from .models import ExportJob

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
        instance.processing_initiated = datetime.now()
        instance.save()
        tasks.run_export_job.delay(instance.pk)

run_export_job_action.short_description = _("Run export job")


def create_export_job_action(modeladmin, request, queryset):
    selected = request.POST.getlist('_selected_action')
    if selected:
        queryset.query.select_related =False
        arbitrary_obj = queryset.first()
        queryset = queryset.only("id")
        selected = queryset.values_list('pk', flat=True)
        ej = ExportJob.objects.create(
            app_label=arbitrary_obj._meta.app_label,
            model=arbitrary_obj._meta.model_name,
            queryset=json.dumps([str(pk) for pk in selected]),
            site_of_origin=request.scheme + "://" + request.get_host()
        )
    queryset.query.select_related = True
    rurl = reverse(
        'admin:%s_%s_change' % (
            ej._meta.app_label,
            ej._meta.model_name,
        ),
        args=[ej.pk],
    )
    return redirect(rurl)


create_export_job_action.short_description = _("Export with celery")
