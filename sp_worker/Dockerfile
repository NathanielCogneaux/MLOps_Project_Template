FROM apache/airflow:2.7.3-python3.11

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /opt/airflow/
COPY src /opt/airflow/src
COPY dags /opt/airflow/dags

WORKDIR /opt/airflow

RUN chown -R airflow:root /opt/airflow/src /opt/airflow/dags /opt/airflow/pyproject.toml

ENV PYTHONPATH="/opt/airflow:${PYTHONPATH}"

USER airflow

RUN pip install --no-cache-dir \
    numpy==1.25.2 \
    pandas==2.1.1

RUN pip install --no-cache-dir -e .
