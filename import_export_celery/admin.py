# -*- coding: utf-8 -*-
# Copyright (C) 2019 o.s. Auto*Mat
from django.contrib import admin
from django.core.cache import cache

from . import models, tasks

@admin.register(models.ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
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
        'change_summary',
        'imported',
        'errors',
        'author',
        'updated_by',
    )

    def job_status_info(self, obj):
        job_status = cache.get('import_job_status_%s' % obj.pk)
        if job_status:
            return job_status
        else:
            return obj.job_status

    actions = (
        tasks.run_import_job_action,
        tasks.run_import_job_action_dry,
    )
