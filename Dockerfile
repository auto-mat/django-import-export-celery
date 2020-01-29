FROM python:3.7
RUN pip3 install poetry celery
RUN apt-get update ; apt-get install -yq python3-psycopg2 gdal-bin
RUN useradd test
RUN chsh test -s /bin/bash
