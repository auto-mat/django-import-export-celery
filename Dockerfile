# Multi-stage build for smaller images
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/proj \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create user
ARG UID=1000
RUN useradd test --uid $UID --create-home --shell /bin/bash

# Install poetry
RUN pip install poetry==1.7.1

# Set working directory
WORKDIR /proj

# Copy dependency files
COPY requirements_test.txt ./

# Install dependencies
RUN pip install -r requirements_test.txt

# Install redis for celery
RUN pip install redis

# Switch to non-root user
USER test
