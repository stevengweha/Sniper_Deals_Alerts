import os
import json
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Charger les variables .env
load_dotenv()

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DB_URL = os.getenv("DB_URL")

def send_to_telegram(message, inline_keyboard=None):
    """Envoie le message formaté HTML et les boutons associés sur Telegram."""
    if not TOKEN or not CHAT_ID:
        print("Erreur: TOKEN ou CHAT_ID manquants dans l'environnement.")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # Payload de base obligatoire
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    # Telegram exige que le reply_markup soit une chaîne JSON sérialisée
    if inline_keyboard:
        payload["reply_markup"] = json.dumps({"inline_keyboard": inline_keyboard})
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur lors de l'envoi Telegram : {e}")
        raise e  # Crucial pour qu'Airflow intercepte le FAIL au lieu de valider en SUCCESS

def main():
    if not DB_URL:
        print("Erreur: DB_URL manquante.")
        return

    try:
        engine = create_engine(DB_URL)
        
        # Requête optimisée
        query = """
        SELECT 
            category, type, title, price, etat, estimated_resell_profit, 
            deal_score, source, url
        FROM public_shopping.final_data 
        WHERE (deal_score LIKE '%%ANOMALIE%%' OR deal_score LIKE '%%EXCELLENT%%')
          AND operational_status != '💤 Obsolète'
          AND data_age_hours <= 24
        ORDER BY category ASC, estimated_resell_profit DESC
        LIMIT 20
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("Aucune opportunité rentable détectée (Modèle à jour mais aucun deal sur 24h).")
            return

        # Récupération des catégories globales pour le découpage visuel
        categories = df['category'].unique()
        
        for cat in categories:
            group = df[df['category'] == cat]
            
            # Un message et un clavier d'inline buttons par MACRO-CATÉGORIE (Évite de dépasser la limite de caractères)
            message = f"🚀 <b>SNIPER | {str(cat).upper()}</b>\n"
            message += f"━━━━━━━━━━━━━━━━━━━\n\n"
            
            inline_keyboard = []
            
            # Utilisation de enumerate pour générer proprement l'index du deal
            for idx, row in enumerate(group.itertuples(), 1):
                # Nettoyage et typage sécurisé via itertuples() pour de meilleures performances
                etat_str = str(getattr(row, 'etat', 'Non spécifié'))
                etat_emoji = "✨" if "Neuf" in etat_str else "📦"
                
                title = str(getattr(row, 'title', 'Sans titre'))[:30]
                p_type = str(getattr(row, 'type', 'Générique'))
                price = float(getattr(row, 'price', 0))
                profit = float(getattr(row, 'estimated_resell_profit', 0))
                url = str(getattr(row, 'url', '#'))
                score = str(getattr(row, 'deal_score', 'N/A'))
                source = str(getattr(row, 'source', 'N/A')).upper()
                
                score_emoji = "💎" if "ANOMALIE" in score else "🔥"
                
                # Formatage HTML
                message += (
                    f"{score_emoji} <b>{title}...</b>\n"
                    f"  🏷️ <b>{p_type}</b> | {price:.0f}€ -> 💸 <b>+{profit:.0f}€ Net</b>\n"
                    f"  {etat_emoji} {etat_str} | 🏪 {source}\n"
                    f"───────────────────\n"
                )
                
                # Ajout du bouton URL dans la structure du clavier
                inline_keyboard.append([{"text": f"⚡ Acheter le Deal #{idx} (+{profit:.0f}€)", "url": url}])
            
            # Envoi du bloc de la catégorie
            send_to_telegram(message, inline_keyboard=inline_keyboard)
            
        print("Pipeline d'alertes exécuté avec succès. Tous les blocs ont été dispatchés.")

    except Exception as e:
        print(f"Erreur lors de l'exécution globale : {str(e)}")
        raise e

if __name__ == "__main__":
    main()