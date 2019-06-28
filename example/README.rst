Install
=======

Install Django dependencies:

.. code-block:: bash

    pipenv install
    pipenv shell

Initialize database tables:

.. code-block:: bash

    python manage.py migrate

Create a super-user for the admin:

.. code-block:: bash

    python manage.py createsuperuser

Run
===

.. code-block:: bash

    python manage.py runserver

The example app will be available from http://127.0.0.1:8000/admin 

Note: parts of this example app were taken from the [djano-leaflet](https://github.com/makinacorpus/django-leaflet/tree/master/example) example app.
