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

The Django server starts automatically after setup. If you need to restart it:

.. code-block:: bash

   docker compose restart web

For debugging or manual control, enter the development container:

.. code-block:: bash

   docker exec -it django-import-export-celery-web-1 bash

Start Celery worker:

**Option 1: Using docker compose (recommended):**

.. code-block:: bash

   docker compose up -d celery

**Option 2: Manual startup (for debugging):**

.. code-block:: bash

   docker exec -it django-import-export-celery-web-1 bash

.. code-block:: bash

   cd example
   export DATABASE_HOST=postgres
   celery -A project worker --loglevel=info -n worker1

The example app will be available from http://localhost:8000/admin/

**Note:** Both Django and Celery need to be running for import/export jobs to work properly.

**Login credentials:**
- Username: admin
- Password: admin

Note: parts of this example app were taken from the [django-leaflet](https://github.com/makinacorpus/django-leaflet/tree/master/example) example app.
