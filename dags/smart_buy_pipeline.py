import os  # 🔥 AJOUTE CET IMPORT TOUT EN HAUT
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.models.param import Param 
from datetime import datetime, timedelta
from pathlib import Path
import pendulum
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, RenderConfig, ExecutionConfig

# Chemin absolu vers dbt
DBT_PROJECT_PATH = Path("/opt/airflow/dbt_project")
os.environ["DBT_TARGET_PATH"] = "/tmp/dbt_target_shopping"

default_args = {
    'owner': 'admin',
    'start_date': datetime(2026, 5, 18),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'smart_buy_sentinel_pipeline',
    default_args=default_args,
    schedule_interval='43 5 * * *',  # Tous les jours à 7h du matin
    catchup=False,
    params={
        "search_query": Param("console, smartphone ", type="string", description="Produit à rechercher")
    }
) as dag:

    # --- ÉTAPE 1 : SCRAPING  ---
    scrape_ebay = BashOperator(
        task_id='scrape_ebay',
        bash_command='python /opt/airflow/scripts/ebay_scraper.py "{{ dag_run.conf.get("search_query", params.search_query) }}"'
    )

    scrape_amazon = BashOperator(
        task_id='scrape_amazon',
        bash_command='python /opt/airflow/scripts/amazon_scraper.py "{{ dag_run.conf.get("search_query", params.search_query) }}"'
    )

    scrape_leboncoin = BashOperator(
        task_id='scrape_leboncoin',
        bash_command='python /opt/airflow/scripts/leboncoin_scraper.py "{{ dag_run.conf.get("search_query", params.search_query) }}"'
    )

    # Cash Express
    scrape_cashexpress = BashOperator(
        task_id='scrape_cashexpress',
        bash_command='python /opt/airflow/scripts/cashexpress_scraper.py "{{ dag_run.conf.get("search_query", params.search_query) }}"'
    )

    
    # --- ÉTAPE 2 : INGESTION SPARK ---
    task_spark_load = SparkSubmitOperator(
        task_id='spark_load_to_postgres',
        application='/opt/spark/spark_jobs/load_to_postgres.py',
        application_args=["{{ dag_run.conf.get('search_query', params.search_query) }}"],
        conn_id='spark_default',
        jars='/opt/spark/drivers/postgresql-42.2.29.jre7.jar',
        conf={
            'spark.master': 'spark://spark-master:7077',
            'spark.driver.extraClassPath': '/opt/spark/drivers/postgresql-42.2.29.jre7.jar'
        }
    )

    # --- ÉTAPE 3 : TRANSFORMATION DBT AVEC COSMOS ---
    dbt_shopping_pipeline = DbtTaskGroup(
        group_id="dbt_transformation_shopping",
        
        project_config=ProjectConfig(
            dbt_project_path=DBT_PROJECT_PATH,
        ),
        
        profile_config=ProfileConfig(
            profile_name="smart_buy",
            target_name="dev",
            profiles_yml_filepath=DBT_PROJECT_PATH / "profiles.yml"
        ),
        
        render_config=RenderConfig(
            select=["tag:shopping"],
        ),
        
        execution_config=ExecutionConfig(
            dbt_executable_path="/usr/local/bin/dbt"
        ),
    )

    # --- Alerter via telegram---
    task_send_deals = BashOperator( 
        task_id='send_deals_telegram',
        bash_command='python /opt/airflow/scripts/send_deals.py'
    )

    # --- DÉFINITION DU FLUX ---
    [scrape_ebay, scrape_amazon, scrape_leboncoin, scrape_cashexpress] >> task_spark_load >> dbt_shopping_pipeline >> task_send_deals