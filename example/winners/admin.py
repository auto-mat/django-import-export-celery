# -*- coding: utf-8 -*-
# Copyright (C) 2016 o.s. Auto*Mat
from django.contrib import admin

from import_export.admin import ImportExportMixin

from . import models


@admin.register(models.Winner)
class WinnerAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        'name',
    )
