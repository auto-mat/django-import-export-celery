.. image:: https://img.shields.io/pypi/v/django-import-export-celery.svg
   :target: https://pypi.org/project/django-import-export-celery/#history

django-import-export-celery: process slow django imports and exports in celery
==============================================================================

django-import-export-celery helps you process long running imports and exports in celery.

Basic installation
------------------

1. `Set up celery <http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html>`__ to work with your project.

2. Add ``'import_export_celery'`` to your ``INSTALLED_APPS`` settings variable

3. Add ``'author.middlewares.AuthorDefaultBackendMiddleware'`` to your ``MIDDLEWARE_CLASSES``

4. Configure the location of your celery module setup

    ::

        IMPORT_EXPORT_CELERY_INIT_MODULE = "projectname.celery"


Setting up imports with celery
------------------------------

A fully configured example project can be found in the example directory of this repository.

1. Perform the basic setup procedure described above.

2.  Configure the IMPORT_EXPORT_CELERY_MODELS variable.

    ::

        def resource():  # Optional
            from myapp.models import WinnerResource
            return WinnerResource


        IMPORT_EXPORT_CELERY_MODELS = {
            "Winner": {
                'app_label': 'winners',
                'model_name': 'Winner',
                'resource': resource,  # Optional
            }
        }

    The available parameters are `app_label`, `model_name`, and `resource`. 'resource' should be a function which returns a django-import-export `Resource <https://django-import-export.readthedocs.io/en/latest/api_resources.html>`__.

3. Done


By default a dry run of the import is initiated when the import object is created. To instead import the file immediately without a dry-run set the `IMPORT_DRY_RUN_FIRST_TIME` to `False`

    ::

        IMPORT_DRY_RUN_FIRST_TIME = False


Preforming an import
--------------------

You will find an example django application that uses django-import-export-celery for importing data. There are instructions for running the example application in the example directory's README file. Once you have it running, you can perform an import with the following steps.

1. Navigate to the example applications admin page:

   .. image:: screenshots/admin.png

2. Navigate to the ImportJobs table:

   .. image:: screenshots/import_jobs.png

3. Create a new import job. There is an example import CSV file in the example/example-data directory. Select that file. Select csv as the file format. We'll be importing to the Winner's model table.

   .. image:: screenshots/new_import_job.png

4. Select "Save and continue editing" to save the import job and refresh until you see that a "Summary of changes made by this import" file has been created.

   .. image:: screenshots/summary.png

5. You can view the summary if you want. Your import has NOT BEEN PERFORMED YET!

   .. image:: screenshots/view-summary.png

6. Return to the import-jobs table, select the import job we just created, and select the "Perform import" action from the actions drop down.

   .. image:: screenshots/perform-import.png

7. In a short time, your imported Winner object should show up in your Winners table.

   .. image:: screenshots/new-winner.png


Setting up exports
------------------

As with imports, a fully configured example project can be found in the `example` directory.

1. Add a `export_resource_classes` classmethod to the model you want to export.
    ::

        @classmethod
        def export_resource_classes(cls):
            return {
                'winners': ('Winners resource', WinnersResource),
                'winners_all_caps': ('Winners with all caps column resource', WinnersWithAllCapsResource),
            }

    This should return a dictionary of tuples. The keys should be unique unchanging strings, the tuples should consist of a `resource <https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource>`__ and a human friendly description of that resource.

2. Add the `create_export_job_action` to the model's `ModelAdmin`.
    ::

        from django.contrib import admin
        from import_export_celery.admin_actions import create_export_job_action

        from . import models


        @admin.register(models.Winner)
        class WinnerAdmin(admin.ModelAdmin):
            list_display = (
                'name',
            )

            actions = (
                create_export_job_action,
            )

3. To customise export queryset you need to add `get_export_queryset` to the `ModelResource`.
    ::

        class WinnersResource(ModelResource):
            class Meta:
                model = Winner

            def get_export_queryset(self):
                """To customise the queryset of the model resource with annotation override"""
                return self.Meta.model.objects.annotate(device_type=Subquery(FCMDevice.objects.filter(
                        user=OuterRef("pk")).values("type")[:1])
4. Done!


Performing exports with celery
------------------------------

1. Perform the basic setup procedure described in the first section.

2. Open up the object list for your model in django admin, select the objects you wish to export, and select the `Export with celery` admin action.

3. Select the file format and resource you want to use to export the data.

4. Save the model

5. You will receive an email when the export is done, click on the link in the email

6. Click on the link near the bottom of the page titled `Exported file`.


Excluding export file formats in the admin site
-----------------------------------------------

All available file formats to export are taken from the `Tablib project <https://pypi.org/project/tablib/>`__.

To exclude or disable file formats from the admin site, configure `IMPORT_EXPORT_CELERY_EXCLUDED_FORMATS` django settings variable. This variable is a list of format strings written in lower case.

    ::

        IMPORT_EXPORT_CELERY_EXCLUDED_FORMATS = ["csv", "xls"]

Customizing File Storage Backend
--------------------------------

Define a custom storage backend by adding the `IMPORT_EXPORT_CELERY_STORAGE` to your Django settings. For instance:

    ::

        IMPORT_EXPORT_CELERY_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

Customizing email template for export job completion email
----------------------------------------------------------

By default this is the subject and template used to send the email


    ::

        Subject: 'Django: Export job completed'
        Email template: 'email/export_job_completion.html'


The default email template can be found `here <https://github.com/auto-mat/django-import-export-celery/blob/master/import_export_celery/templates/email/export_job_completion.html>`__

The default email subject and template can be customized by overriding these values from django settings:-


    ::

        EXPORT_JOB_COMPLETION_MAIL_SUBJECT="Your custom subject"
        EXPORT_JOB_COMPLETION_MAIL_TEMPLATE="path_to_folder/your_custom_template.html"


The email template will get some context variables that you can use to customize your template.


    ::

        {
            export_job: The current instance of ExportJob model
            app_label: export_job.app_label
            model: export_job.model
            link: A link to go to the export_job instance on django admin
        }


For developers of this library
------------------------------

You can enter a preconfigured dev environment by first running `make` and then launching `./develop.sh` to get into a docker compose environment packed with **redis**, **celery**, **postgres** and everything you need to run and test django-import-export-celery.

Before submitting a PR please run `flake8` and (in the examples directory) `python3 manange.py test`.

Please note, that you need to restart celery for changes to propogate to the workers. Do this with `docker-compose down celery`, `docker-compose up celery`.

Commercial support
------------------

Commercial support is provided by `gradesta s.r.o <https://gradesta.com/support/>`_.

Credits
-------

`django-import-export-celery` was developed by the Czech non-profit `auto*mat z.s. <https://auto-mat.cz>`_.
