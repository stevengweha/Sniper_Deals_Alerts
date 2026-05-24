import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Chargement des configs
load_dotenv()
DB_URL = os.getenv("DB_URL")
MONGO_URI = os.getenv("MONGODB_URI")
TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_USERNAME = "Bestdeal_sniperbot"

def get_all_users():
    """Récupère tous les IDs Telegram depuis MongoDB et les convertit en entiers."""
    try:
        client = MongoClient(MONGO_URI)
        db = client["smart_buy_db"]
        users = list(db["users"].find({}, {"telegramId": 1}))
        # Conversion forcée en entier pour éviter le .0
        return [int(u['telegramId']) for u in users if 'telegramId' in u]
    except Exception as e:
        print(f"Erreur connexion MongoDB : {e}")
        return []

def send_to_all_users(message, users):
    """Envoie le message avec gestion du contexte (Privé vs Groupe)"""
    for chat_id in users:
        is_group = chat_id < 0
        
        if is_group:
            bot_url = f"https://t.me/{BOT_USERNAME}?start=app"
            reply_markup = {
                "inline_keyboard": [[
                    {"text": "🚀 Lancer la Mini-App", "url": bot_url}
                ]]
            }
        else:
            reply_markup = {
                "inline_keyboard": [[
                    {"text": "🚀 Ouvrir la Mini-App", "web_app": {"url": "https://sniper-deals-alerts.vercel.app/"}}
                ]]
            }

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": reply_markup
        }

        try:
            response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
            if response.status_code == 200:
                print(f"✅ Succès pour {chat_id}")
            else:
                print(f"❌ Échec pour {chat_id} (Code {response.status_code}): {response.text}")
        except Exception as e:
            print(f"❌ Erreur réseau pour {chat_id}: {e}")

def format_and_send_category_alert(category_name, df_category, user_list):
    if df_category.empty or not user_list:
        return

    message = f"📦 <b>OFFRES : {category_name.upper()}</b>\n"
    message += "🔥 <i>Le Top 10 par profitabilité</i>\n"
    message += "━━━━━━━━━━━━━━━━━━━━━\n\n"

    for idx, row in df_category.iterrows():
        title = str(row.get('title', 'Produit inconnu'))[:35]
        url = row.get('url', '#')
        price = float(row.get('price', 0))
        market_price = float(row.get('median_model_price', 0))
        profit = float(row.get('estimated_resell_profit', 0))
        ops_status = str(row.get('operational_status', ''))
        # CORRECTION : Extraction correcte de la condition
        condition = str(row.get('product_condition', 'Non spécifié'))

        sniper_badge = "🚨 <b>SNIPER FLIP !</b>\n" if "SNIPER" in ops_status.upper() else ""
        
        message += f"{sniper_badge}<b>{idx + 1}. <a href='{url}'>{title}...</a></b>\n"
        message += f"💰 <b>{price:,.0f}€</b> au lieu de ~{market_price:,.0f}€\n"
        message += f"📈 Bénéfice : <b>+{profit:,.0f}€</b>\n"
        message += f"🏷️ État : {condition}\n"
        message += "─────────────────────\n"

    send_to_all_users(message, user_list)

def main():
    user_list = get_all_users()
    if not user_list:
        return

    engine = create_engine(DB_URL)
    # Requête avec partitionnement SQL pour éviter les biais
    query = """
        WITH ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY category 
                    ORDER BY 
                        (CASE WHEN operational_status LIKE '%%SNIPER%%' THEN 1 ELSE 2 END),
                        (CASE WHEN deal_score LIKE '%%EXCELLENT%%' THEN 1 
                              WHEN deal_score LIKE '%%BON%%' THEN 2 ELSE 3 END),
                        estimated_resell_profit DESC
                ) as rnk
            FROM public_shopping.final_data
            WHERE statistical_confidence != '🔴 Faible'
              AND (deal_score LIKE '%%EXCELLENT%%' OR deal_score LIKE '%%BON%%' OR operational_status LIKE '%%SNIPER%%')
        )
        SELECT * FROM ranked WHERE rnk <= 10
    """

    df = pd.read_sql(query, engine)
    
    if df.empty:
        return

    df = df.fillna("Non spécifié")

    # On itère sur les catégories retournées par la requête déjà filtrée
    for cat in df['category'].unique():
        df_cat = df[df['category'] == cat]
        format_and_send_category_alert(cat, df_cat, user_list)

if __name__ == "__main__":
    main()