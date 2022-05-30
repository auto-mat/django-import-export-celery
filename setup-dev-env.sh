#!/bin/bash
cd example
poetry install
poetry run python3 manage.py migrate
