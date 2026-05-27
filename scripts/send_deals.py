import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
from dotenv import load_dotenv
import time

# 1. Chargement des configs
load_dotenv()
DB_URL = os.getenv("DB_URL")
MONGO_URI = os.getenv("MONGODB_URI")
TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_USERNAME = "Bestdeal_sniperbot"

def get_all_group_channels():
    try:
        client = MongoClient(MONGO_URI)
        db = client["smart_buy_db"]
        users = list(db["users"].find({}, {"telegramId": 1}))
        return [int(u['telegramId']) for u in users if 'telegramId' in u and int(u['telegramId']) < 0]
    except Exception as e:
        print(f"Erreur connexion MongoDB : {e}")
        return []

def send_article_via_photo(message, url, group_list):
    """Envoie une photo puis bascule en texte si la photo échoue."""
    for chat_id in group_list:
        payload = {
            "chat_id": chat_id,
            "photo": url,
            "caption": message,
            "parse_mode": "HTML"
        }
        # Tente l'envoi en photo
        res = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", json=payload)
        
        # Fallback si l'image ne passe pas : envoi en texte simple pour forcer l'aperçu
        if res.status_code != 200:
            fallback_payload = {
                "chat_id": chat_id,
                "text": message + f"\n\n🔗 {url}",
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=fallback_payload)
        
        time.sleep(1.0) # Pause pour respecter les limites Telegram

def send_final_button(group_list):
    """Envoi du bouton MiniApp en message séparé."""
    for chat_id in group_list:
        payload = {
            "chat_id": chat_id,
            "text": "🚀 <b>Accéder au articles Complet</b>",
            "parse_mode": "HTML",
            "reply_markup": {
                "inline_keyboard": [[{"text": "Ouvrir la MiniApp", "url": f"https://t.me/{BOT_USERNAME}?start=app"}]]
            }
        }
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
        time.sleep(0.5)

def main():
    group_list = get_all_group_channels()
    if not group_list:
        return

    engine = create_engine(DB_URL)
    
    # Requête ciblée sur les nouveautés (dernière heure)
    query = """
        SELECT * FROM public_shopping.final_data
        WHERE statistical_confidence != '🔴 Faible'
          AND (deal_score LIKE '%%EXCELLENT%%' OR deal_score LIKE '%%BON%%' OR operational_status LIKE '%%SNIPER%%' OR operational_status LIKE '%%ACTIF%%')
          AND data_age_hours <= 1.0
        ORDER BY timestamp DESC
        LIMIT 10
    """

    df = pd.read_sql(query, engine)
    if df.empty:
        return
    df = df.fillna("Non spécifié")
    
    print(f"Envoi de {len(df)} deals qualifiés vers Telegram...")
    
    # Envoi des articles un par un
    for _, row in df.iterrows():
        title = str(row.get('title', 'Produit inconnu'))
        url = row.get('url', '#')
        price = float(row.get('price', 0))
        market_price = float(row.get('median_model_price', 0))
        profit = float(row.get('estimated_resell_profit', 0))
        source = str(row.get('source', 'Inconnu'))
        ops_status = str(row.get('operational_status', ''))
        etat = str(row.get('product_condition', ''))
        
        sniper_badge = "🚨 <b>SNIPER FLIP !</b> " if "SNIPER" in ops_status.upper() else "✨ "
        
        message = f"{sniper_badge}\n\n"
        message += f"<a href='{url}'><b>{title}</b></a>\n\n"
        message += f"💰 <b>{price:,.0f}€</b> Au lieu de {market_price:,.0f}€\n"
        message += f"📈 Gain estimé: <b>+{profit:,.0f}€</b>\n"
        message += f"📦 Source : {source}\n"
        message += f"♻️etat : {etat}"
        
        send_article_via_photo(message, url, group_list)

    # Bouton final (sorti de la boucle)
    send_final_button(group_list)

if __name__ == "__main__":
    main()