# -*- coding: utf-8 -*-
# Copyright (C) 2019 o.s. Auto*Mat
from django import forms
from django.contrib import admin
from django.core.cache import cache

from . import admin_actions, models


class JobWithStatusMixin:
    def job_status_info(self, obj):
        job_status = cache.get(self.direction + '_job_status_%s' % obj.pk)
        if job_status:
            return job_status
        else:
            return obj.job_status


@admin.register(models.ImportJob)
class ImportJobAdmin(JobWithStatusMixin, admin.ModelAdmin):
    direction = 'import'
    list_display = (
        'model',
        'job_status_info',
        'file',
        'change_summary',
        'imported',
        'author',
        'updated_by',
    )
    readonly_fields = (
        'job_status_info',
        'change_summary',
        'imported',
        'errors',
        'author',
        'updated_by',
    )
    exclude = ('job_status', )

    actions = (
        admin_actions.run_import_job_action,
        admin_actions.run_import_job_action_dry,
    )


class ExportJobForm(forms.ModelForm):
    class Meta:
        model = models.ExportJob
        exclude = (
            'site_of_origin',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resource'].widget = forms.Select(choices=self.instance.get_resource_choices())


@admin.register(models.ExportJob)
class ExportJobAdmin(JobWithStatusMixin, admin.ModelAdmin):
    direction = 'export'
    form = ExportJobForm
    list_display = (
        'model',
        'app_label',
        'file',
        'job_status_info',
        'author',
        'updated_by',
    )
    readonly_fields = (
        'job_status_info',
        'author',
        'updated_by',
        'app_label',
        'model',
        'file',
        'processing_initiated',
    )
    exclude = ('job_status', )

    def has_add_permission(self, request, obj=None):
        return False

    actions = (
        admin_actions.run_export_job_action,
    )
