from pyspark.sql import SparkSession
import os

def main():
    spark = SparkSession.builder.appName("Ingest_SNCF_Frequentation").getOrCreate()
    file_path = "/opt/airflow/data/raw/transport-train/frequentation-gares.json"

    if os.path.exists(file_path):
        print(f"🚀 Ingestion Fréquentation JSON...")

        # Lecture JSON avec gestion du multi-ligne
        df = spark.read.option("multiline", "true").json(file_path)
        
        
        df.write.format("jdbc") \
            .option("url", "jdbc:postgresql://postgres_data:5432/smart_buy_db") \
            .option("dbtable", "raw_sncf_frequentation") \
            .option("user", "admin").option("password", "admin") \
            .option("driver", "org.postgresql.Driver") \
            .mode("overwrite").save()
        print("✅ Table raw_sncf_frequentation créée.")

    spark.stop()

if __name__ == "__main__":
    main()