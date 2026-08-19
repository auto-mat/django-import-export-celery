import json

from django.db import migrations, models


def normalize_queryset_values(apps, schema_editor):
    """Every row must hold valid JSON (a list or dict) before the column
    becomes a JSONField; anything else becomes an empty pk list."""
    ExportJob = apps.get_model("import_export_celery", "ExportJob")
    for job in ExportJob.objects.all().iterator():
        try:
            parsed = json.loads(job.queryset)
        except (TypeError, ValueError):
            parsed = None
        if not isinstance(parsed, (list, dict)):
            ExportJob.objects.filter(pk=job.pk).update(queryset="[]")


class Migration(migrations.Migration):

    dependencies = [
        ("import_export_celery", "0013_exportjob_resource_kwargs"),
    ]

    operations = [
        migrations.RunPython(normalize_queryset_values, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="exportjob",
            name="queryset",
            field=models.JSONField(
                default=list,
                verbose_name="JSON list of pks to export or dict of queryset filters",
            ),
        ),
    ]
