Install
=======

Quick setup with make:

.. code-block:: bash

   make

Or manual setup:

.. code-block:: bash

   docker compose up -d postgres redis
   docker compose up -d web
   docker exec django-import-export-celery-web-1 /proj/setup-dev-env.sh

Run
===

Enter the development container:

.. code-block:: bash

   docker exec -it django-import-export-celery-web-1 bash

Run the Django server:

.. code-block:: bash

   cd example
   export DATABASE_HOST=postgres
   python manage.py runserver 0.0.0.0:8000

The example app will be available from http://localhost:8001/admin

**Login credentials:**
- Username: admin
- Password: admin

Note: parts of this example app were taken from the [django-leaflet](https://github.com/makinacorpus/django-leaflet/tree/master/example) example app.
