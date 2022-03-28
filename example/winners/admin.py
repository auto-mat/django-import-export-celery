# Copyright (C) 2016 o.s. Auto*Mat
from django.contrib import admin

from import_export.admin import ImportExportMixin
from import_export_celery.admin_actions import create_export_job_action

from . import models


@admin.register(models.Winner)
class WinnerAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name",)

    actions = (create_export_job_action,)
