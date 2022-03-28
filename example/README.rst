Install
=======

Launch docker-compose

.. code-block:: bash

   docker-compose up

Attach to docker-compose

.. code-block:: bash

   docker attach djangoimportexportcelery_web

Install Django dependencies:

.. code-block:: bash

    cd example
    pipenv install
    pipenv shell

Initialize database tables:

.. code-block:: bash

    python manage.py migrate

Create a super-user for the admin:

.. code-block:: bash

    python manage.py createsuperuser

Restart docker-compose

.. code-block:: bash

   docker-compose down


Run
===

Launch docker-compose

.. code-block:: bash

   docker-compose up

Attach to docker-compose

.. code-block:: bash

   docker attach djangoimportexportcelery_web

Enter pipenv shell:

.. code-block:: bash

    cd example
    pipenv shell


Actually run the server

.. code-block:: bash

    python manage.py runserver 0.0.0.0:8000

The example app will be available from http://127.0.0.1:8001/admin

Note: parts of this example app were taken from the [djano-leaflet](https://github.com/makinacorpus/django-leaflet/tree/master/example) example app.
