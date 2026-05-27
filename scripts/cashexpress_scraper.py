import os
import sys
import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests
import random

# CONFIGURATION DES ROUTES DE SCRAPING (URL, Catégorie et Marque Injectées)
SCRAPING_ROUTES = {
    "iphone": {
        "url_template": "https://www.cashexpress.fr/produits-occasions/telephonie-mobile,40/iphone,1001/page,{offset}.html",
        "category": "SMARTPHONE",
        "brand": "APPLE"
    },
    "playstation": {
        "url_template": "https://www.cashexpress.fr/produits-occasions/console-sony,53/page,{offset}.html",
        "category": "CONSOLE",
        "brand": "SONY"
    },
    "xbox": {
        "url_template": "https://www.cashexpress.fr/produits-occasions/console-microsoft,58/page,{offset}.html",
        "category": "CONSOLE",
        "brand": "MICROSOFT"
    },
    "samsung": {
        "url_template": "https://www.cashexpress.fr/produits-occasions/telephonie-mobile,40/samsung,1002/page,{offset}.html",
        "category": "SMARTPHONE",
        "brand": "SAMSUNG"
    },
    "laptop": {
        "url_template": "https://www.cashexpress.fr/produits-occasions/ordinateur-portable,36/page,{offset}.html",
        "category": "ORDINATEUR",
        "brand": "laptop"
    }
}

def scrape_cashexpress_category(route_key, target_count):
    config = SCRAPING_ROUTES.get(route_key.lower())
    if not config:
        print(f"❌ Aucune route configurée pour la clé : {route_key}")
        return

    print(f"🎯 [ROUTAGE PAR CATÉGORIE] Extraction : {config['category']} | Marque : {config['brand']}")
    all_items = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    
    current_page = 1
    
    with requests.Session(impersonate="chrome120") as session:
        while len(all_items) < target_count:
            # Calcul de l'offset exigé par l'URL Cash Express (0, 16, 32...)
            offset = (current_page - 1) * 16
            url = config["url_template"].format(offset=offset)
            
            print(f"📡 Requête Page {current_page} (Offset {offset}) -> {url}")
            
            try:
                response = session.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    print(f"❌ Erreur serveur ou fin de catalogue ({response.status_code})")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                product_cards = soup.find_all("div", class_="item_produit_magasin")
                
                if not product_cards:
                    print("🏁 Aucun produit trouvé sur cette page. Fin du catalogue.")
                    break
                
                items_found_this_page = 0
                for card in product_cards:
                    if len(all_items) >= target_count:
                        break
                    
                    # 1. Extraction du Titre et de l'URL
                    h3_element = card.find("h3")
                    if not h3_element: continue
                        
                    a_element = h3_element.find("a")
                    if not a_element: continue
                        
                    title = a_element.text.strip().upper()
                    href = a_element.get("href", "")
                    url_product = f"https://www.cashexpress.fr{href}"
                    
                    # Filtre de sécurité basique (conservé mais dbt fera le gros du travail)
                    if any(p in title.lower() for p in ["telecommande", "support", "cable", "fixation"]):
                        continue
                    
                    # 2. Extraction du Prix 
                    price_element = card.find("span", class_="prix")
                    if not price_element: continue
                    price_raw = price_element.text.strip()
                    
                    # Enclenchement du payload enrichi
                    all_items.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "CASH_EXPRESS",
                        "injected_category": config["category"],  
                        "injected_brand": config["brand"],        
                        "title": title,
                        "price_raw": price_raw,
                        "url": url_product
                    })
                    items_found_this_page += 1
                
                print(f"📊 Page {current_page} complétée : +{items_found_this_page} lignes ({len(all_items)}/{target_count})")
                
                if items_found_this_page == 0:
                    break
                    
                current_page += 1
                time.sleep(1) 
                
            except Exception as e:
                print(f"💥 Incident de parsing sur la page {current_page} : {e}")
                break

    if all_items:
        df = pd.DataFrame(all_items)
        output_dir = "/opt/airflow/data/raw/shopping"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"cashexpress_{route_key.lower()}.csv"
        full_path = os.path.join(output_dir, filename)
        
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"✨ [SUCCÈS] {len(df)} lignes générées dans : {full_path}")
    else:
        print(f"❌ Aucune donnée pour la route : {route_key}")

if __name__ == "__main__":
    # On peut passer une liste de routes à scraper en argument, séparées par des virgules (ex: "iphone,playstation")
    input_str = sys.argv[1] if len(sys.argv) > 1 else "iphone,playstation,xbox,samsung,laptop"
    routes_to_run = [r.strip() for r in input_str.split(',')]
    
    for route in routes_to_run:
        scrape_cashexpress_category(route, target_count=500)
        
        # Pause de sécurité anti-ban
        sleep_between_queries = random.uniform(20, 40)
        print(f"💤 Pause de sécurité de {int(sleep_between_queries)}s...")
        time.sleep(sleep_between_queries)