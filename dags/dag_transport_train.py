import os  # 🔥 Essentiel pour l'isolation globale
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
from pathlib import Path
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, RenderConfig, ExecutionConfig

# Chemin absolu vers dbt
DBT_PROJECT_PATH = Path("/opt/airflow/dbt_project")
os.environ["DBT_TARGET_PATH"] = "/tmp/dbt_target_transport_train"

default_args = {
    'owner': 'admin',
    'start_date': datetime(2026, 5, 14),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

with DAG(
    'transport_train_pipeline',
    default_args=default_args,
    description='Pipeline SNCF : Ingestion Spark -> Transformations dbt (Cosmos)',
    schedule_interval='@daily',
    catchup=False
) as dag:

    # --- ÉTAPE 1a : INGESTION (CSV) ---
    task_spark_regularite = SparkSubmitOperator(
        task_id='spark_load_sncf_regularite',
        application='/opt/spark/spark_jobs/load_sncf_regularite.py',
        conn_id='spark_default',
        jars='/opt/spark/drivers/postgresql-42.2.29.jre7.jar',
        conf={
            'spark.master': 'spark://spark-master:7077',
            'spark.driver.extraClassPath': '/opt/spark/drivers/postgresql-42.2.29.jre7.jar'
        }
    )

    # --- ÉTAPE 1b : INGESTION  (JSON) ---
    task_spark_frequentation = SparkSubmitOperator(
        task_id='spark_load_sncf_frequentation',
        application='/opt/spark/spark_jobs/load_sncf_frequentation.py',
        conn_id='spark_default',
        jars='/opt/spark/drivers/postgresql-42.2.29.jre7.jar',
        conf={
            'spark.master': 'spark://spark-master:7077',
            'spark.driver.extraClassPath': '/opt/spark/drivers/postgresql-42.2.29.jre7.jar'
        }
    )
    
    # --- ÉTAPE 2, 3 & 4 :  Transformation DBT avec Cosmos ---
    dbt_transport_pipeline = DbtTaskGroup(
        group_id="dbt_transformation_transport",
        
        project_config=ProjectConfig(
            dbt_project_path=DBT_PROJECT_PATH,
        ),
        
        profile_config=ProfileConfig(
            profile_name="smart_buy",
            target_name="dev",
            profiles_yml_filepath=DBT_PROJECT_PATH / "profiles.yml"
        ),
        
        render_config=RenderConfig(
            select=["path:models/transport-train"]
        ),
        
        execution_config=ExecutionConfig(
            dbt_executable_path="/usr/local/bin/dbt"
        ),
    )

    # --- DÉFINITION DU FLUX ---
    [task_spark_regularite, task_spark_frequentation] >> dbt_transport_pipeline