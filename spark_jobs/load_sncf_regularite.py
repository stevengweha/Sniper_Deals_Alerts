from pyspark.sql import SparkSession
import os
import sys

def main():
    spark = SparkSession.builder.appName("Transport_To_Public").getOrCreate()
    
    # On cible le dossier transport
    raw_dir = "/opt/airflow/data/raw/transport-train"

    if not os.path.exists(raw_dir):
        print(f"❌ Dossier transport introuvable : {raw_dir}")
        return

    files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    
    if not files:
        print("Empty folder: Nothing to ingest for transport.")
        return

    for file_name in files:
        file_path = os.path.join(raw_dir, file_name)
        
        # On décide de la table cible en fonction du nom du fichier
        if "sncf" in file_name.lower():
            target_table = "raw_sncf"
        else:
            target_table = "raw_sncf_regularite"

        print(f"🚀 Ingestion : {file_name} -> {target_table} (Schéma PUBLIC)...")

        try:
            # Lecture du CSV 
            df = spark.read.option("sep", ";").option("header", "True").csv(file_path, inferSchema=True)
            
            df.write \
                .format("jdbc") \
                .option("url", "jdbc:postgresql://postgres_data:5432/smart_buy_db") \
                .option("dbtable", target_table) \
                .option("user", "admin") \
                .option("password", "admin") \
                .option("driver", "org.postgresql.Driver") \
                .mode("overwrite") \
                .save()
            
            print(f"✅ Terminé : {target_table}")
            
        except Exception as e:
            print(f"💥 Erreur lors du traitement de {file_name} : {e}")
            raise e

    spark.stop()

if __name__ == "__main__":
    main()