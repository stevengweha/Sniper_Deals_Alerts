import os
import sys
import shutil
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, current_timestamp, lit

def main():
    print("🚀 [START] Initialisation du Pipeline d'Ingestion PySpark")

    # 1. Récupération des variables d'environnement de ton .env
    DB_HOST = os.environ.get("POSTGRES_HOST")
    DB_PORT = os.environ.get("POSTGRES_PORT")
    DB_NAME = os.environ.get("POSTGRES_DB")
    DB_USER = os.environ.get("POSTGRES_USER")
    DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

    # 2. Initialisation avec le JAR local
    spark = SparkSession.builder \
        .appName("SmartBuy_AutoIngest") \
        .config("spark.jars", "/opt/airflow/drivers/postgresql-42.2.29.jre7.jar") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")

    raw_dir = "/opt/airflow/data/raw/shopping"
    files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    
    if not files:
        print("Empty folder: Nothing to ingest.")
        spark.stop()
        return

    for file_name in files:
        file_path = os.path.join(raw_dir, file_name)
        
        # Détermination de la table cible
        if file_name.startswith("lbc_"):
            target_table = "raw_leboncoin"
        elif file_name.startswith("ebay_"):
            target_table = "raw_ebay"
        elif file_name.startswith("cashexpress_"):
            target_table = "raw_cashexpress"
        else:
            continue

        print(f"🚀 Ajout de {file_name} vers {target_table}...")

        try:
            # 1. Lecture du CSV
            df = spark.read.csv(file_path, header=True, inferSchema=True)
            
            # 2. Nettoyage linéaire du Prix
            df_cleaned = df.withColumn("price_tmp", regexp_replace(col("price_raw"), r"[\s\u00a0$€£a-zA-Z]", ""))
            df_cleaned = df_cleaned.withColumn("price_tmp", regexp_replace(col("price_tmp"), r"\.(?=\d{3})", ""))
            df_cleaned = df_cleaned.withColumn("price_tmp", regexp_replace(col("price_tmp"), r",(?=\d{3})", ""))
            df_cleaned = df_cleaned.withColumn("price_tmp", regexp_replace(col("price_tmp"), ",", "."))
            df_cleaned = df_cleaned.withColumn("price_cleaned", col("price_tmp").cast("float"))
            
            # 3. Enrichissement (On utilise les colonnes déjà présentes dans ton CSV)
            df_final = df_cleaned.withColumn("ingested_at", current_timestamp()) \
                     .select(
                         col("timestamp"),
                         col("ingested_at"),
                         col("source"),
                         col("injected_category").alias("category"), 
                         col("injected_brand").alias("brand"),       
                         col("title"),
                         col("price_raw"),
                         col("price_cleaned"),
                         col("url")
                     )

            # 4. Écriture JDBC dans Postgres
            df_final.write \
                .format("jdbc") \
                .option("url", f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}") \
                .option("dbtable", f"public.{target_table}") \
                .option("user", DB_USER) \
                .option("password", DB_PASSWORD) \
                .option("driver", "org.postgresql.Driver") \
                .mode("append") \
                .save()
            
            print(f"✅ Données ajoutées avec succès dans {target_table}")
            
            # 5. ARCHIVAGE UNIQUEMENT SI TOUT EST OK
            processed_base_path = "/opt/airflow/data/processed/used-data-shop"
            os.makedirs(processed_base_path, exist_ok=True)

            if os.path.exists(file_path):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = os.path.join(processed_base_path, f"{ts}_{file_name}")
                shutil.move(file_path, dest_path)
                print(f"📦 Archivé avec succès : {file_name} -> {processed_base_path}")
            else:
                print(f"⚠️ Fichier introuvable pour archivage : {file_name}")
            
        except Exception as e:
            print(f"💥 Erreur critique lors du traitement de {file_name} : {e}")
            print(f"❌ Le fichier {file_name} n'a pas été archivé et reste dans le dossier 'raw'.")
            continue

    spark.stop()
    print("🏁 [END] Pipeline terminé.")

if __name__ == "__main__":
    main()