import codecs
import os
from setuptools import setup, find_packages
import subprocess
import datetime

here = os.path.abspath(os.path.dirname(__file__))

requires = ["Django", "django-import-export", "django-author", "html2text"]

try:
    version = (
        subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
        .decode("utf-8")
        .strip()
    )
except subprocess.CalledProcessError:
    version = "0.dev" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

setup(
    name="django-import-export-celery",
    version=version,
    author="Timothy Hobbs",
    author_email="timothy.hobbs@auto-mat.cz",
    url="https://github.com/auto-mat/django-import-export-celery",
    download_url="http://pypi.python.org/pypi/django-import-export-celery/",
    description="Process long running django imports and exports in celery",
    long_description=codecs.open(
        os.path.join(here, "README.rst"), "r", "utf-8"
    ).read(),
    long_description_content_type="text/x-rst",
    license=(
        "License :: OSI Approved :: GNU Lesser General Public License v3.0 or"
        " later (LGPLv3.0+)"
    ),
    install_requires=requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Topic :: Utilities",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
