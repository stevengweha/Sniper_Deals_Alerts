from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp
import shutil
from datetime import datetime
import os
import sys

def main():
    spark = SparkSession.builder.appName("SmartBuy_AutoIngest").getOrCreate()
    raw_dir = "/opt/airflow/data/raw/shopping"

    # Récupération du mot-clé passé par Airflow (sys.argv[1])
    search_query = sys.argv[1] if len(sys.argv) > 1 else "unknown"

    files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    
    if not files:
        print("Empty folder: Nothing to ingest.")
        return

    for file_name in files:
        file_path = os.path.join(raw_dir, file_name)
        
        if file_name.startswith("lbc_"):
            target_table = "raw_leboncoin"
        elif file_name.startswith("ebay_"):
            target_table = "raw_ebay"
        elif file_name.startswith("amazon_"): 
            target_table = "raw_amazon"
        elif file_name.startswith("cashexpress_"):
            target_table = "raw_cashexpress"
        else:
            continue

        print(f"🚀 Ajout de {file_name} (Recherche: {search_query}) vers {target_table}...")

        try:
            # 1. Lecture
            df = spark.read.csv(file_path, header=True, inferSchema=True)
            
            # 2. Enrichissement : On ajoute le mot-clé de recherche et un timestamp d'ingestion
            df_final = df.withColumn("search_keyword", lit(search_query)) \
                         .withColumn("ingested_at", current_timestamp())

            # 3. ÉCRITURE EN MODE APPEND pour ne pas écraser les données précédentes
            df_final.write \
                .format("jdbc") \
                .option("url", "jdbc:postgresql://postgres_data:5432/smart_buy_db") \
                .option("dbtable", f"public.{target_table}") \
                .option("user", "admin") \
                .option("password", "admin") \
                .option("driver", "org.postgresql.Driver") \
                .mode("append") \
                .save()
            
            print(f"✅ Données ajoutées avec succès dans {target_table}")
            
           
        except Exception as e:
            print(f"💥 Erreur : {e}")
        finally:
            # 4. ARCHIVAGE UNIQUE : On envoie vers le dossier final
            processed_base_path = "/opt/airflow/data/processed/used-data-shop"
            os.makedirs(processed_base_path, exist_ok=True)

            try:
                if os.path.exists(file_path):
                    # ajoute le timestamp pour éviter d'écraser les fichiers déjà archivés
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_path = os.path.join(processed_base_path, f"{ts}_{file_name}")
                    
                    shutil.move(file_path, dest_path)
                    print(f"📦 Archivé avec succès : {file_name} -> {processed_base_path}")
                else:
                    print(f"⚠️ Fichier introuvable pour archivage : {file_name}")
            except Exception as archive_error:
                print(f"⚠️ Erreur lors de l'archivage : {archive_error}")

    spark.stop()

if __name__ == "__main__":
    main()