FROM python:3.7
RUN pip3 install poetry celery
RUN apt-get update ; apt-get install -yq python3-psycopg2 gdal-bin
ARG UID
RUN useradd test --uid $UID
RUN chsh test -s /bin/bash
