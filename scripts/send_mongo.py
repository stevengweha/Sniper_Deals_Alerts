import os
import pandas as pd
import numpy as np
from pymongo import MongoClient, ReplaceOne
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def push_best_deals():
    db_url = os.getenv('DB_URL')
    mongo_uri = os.getenv('MONGODB_URI')
    
    # 1. Requête SQL Filtrée : 
    # On ne récupère QUE les deals "💎" ou "🔥" 
    # ET avec une confiance statistique "Moyenne" ou "Élevée" (🟡 ou 🟢)
    query = """
        SELECT * FROM public_shopping.final_data
        WHERE (deal_score LIKE '%%💎%%' OR deal_score LIKE '%%🔥%%')
        AND (statistical_confidence LIKE '%%Moyenne%%' OR statistical_confidence LIKE '%%Élevée%%')
    """
    
    try:
        logger.info("Lecture des deals qualifiés depuis Postgres...")
        df = pd.read_sql(query, db_url)
    except Exception as e:
        logger.error(f"Impossible de lire la table Postgres : {e}")
        return

    if df.empty:
        logger.info("Aucun deal qualifié trouvé.")
        return

    logger.info(f"Transfert de {len(df)} deals fiables vers MongoDB...")

    # 2. Push vers MongoDB via BulkWrite (beaucoup plus rapide qu'un update_one par ligne)
    try:
        client = MongoClient(mongo_uri)
        db = client['smart_buy_db']
        collection = db['deals']

        operations = []
        for _, row in df.iterrows():
            data = row.replace({np.nan: None}).to_dict()
            
            # On prépare l'upsert : si l'URL existe, on écrase, sinon on crée.
            # L'avantage est qu'on envoie tout en un seul bloc réseau à la fin.
            operations.append(
                ReplaceOne({"url": data["url"]}, data, upsert=True)
            )
        
        if operations:
            result = collection.bulk_write(operations)
            logger.info(f"Synchronisation terminée : {result.upserted_count} créés, {result.modified_count} mis à jour.")
        
        client.close()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi vers MongoDB : {e}")

if __name__ == "__main__":
    push_best_deals()