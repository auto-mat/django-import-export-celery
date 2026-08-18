from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("import_export_celery", "0012_alter_exportjob_id_alter_importjob_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="exportjob",
            name="resource_kwargs",
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name="JSON dict of kwargs for the resource constructor",
            ),
        ),
    ]
