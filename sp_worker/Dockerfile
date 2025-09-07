FROM apache/airflow:2.7.3-python3.11

# Switch to root to install system dependencies and Python packages
USER root

# Install OS-level dependencies for compiling some packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml /opt/airflow/
COPY src /opt/airflow/src
COPY dags /opt/airflow/dags

WORKDIR /opt/airflow

# Fix ownership
RUN chown -R airflow:root /opt/airflow/src /opt/airflow/dags /opt/airflow/pyproject.toml

# Set PYTHONPATH so Airflow sees your package
ENV PYTHONPATH="/opt/airflow:${PYTHONPATH}"

# Switch to airflow user
USER airflow

# Step 1: Install critical C-extension packages first (ensure binary compatibility)
RUN pip install --no-cache-dir \
    numpy==1.25.2 \
    pandas==2.1.1

# Step 2: Install your package (this installs other dependencies from pyproject.toml)
RUN pip install --no-cache-dir -e .
