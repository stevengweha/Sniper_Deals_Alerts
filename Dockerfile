FROM apache/airflow:2.8.0
USER root
# Installation de Java pour Spark
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
USER airflow
# Installation des connecteurs
RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-spark==4.0.0 \
    psycopg2-binary \
    pyspark==3.5.0\
    dbt-postgres \
    cloudscraper \
    beautifulsoup4 \
    pandas \
    astronomer-cosmos\
    curl_cffi\
    