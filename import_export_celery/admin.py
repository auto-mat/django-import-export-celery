# -*- coding: utf-8 -*-
# Copyright (C) 2019 o.s. Auto*Mat
from django.contrib import admin

from . import models

@admin.register(models.ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = (
        'model',
        'file',
        'change_summary',
        'imported',
        'author',
        'updated_by',
    )
    readonly_fields = (
        'change_summary',
        'imported',
        'processing_initiated',
        'errors',
        'author',
        'updated_by',
    )
