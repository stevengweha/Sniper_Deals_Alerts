import os
import sys
import time
import pandas as pd
from datetime import datetime
import cloudscraper
from bs4 import BeautifulSoup
import random

# CONFIGURATION DES ROUTES CHIRURGICALES LEBONCOIN
# category=17 (Téléphonie) | shippable=1 (Livraison disponible) | price=80-max (Anti-pollution accessoires)
SCRAPING_ROUTES = {
    "iphone": {
        "url_template": "https://www.leboncoin.fr/recherche?category=17&shippable=1&price=80-max&phone_brand=apple&page={page}",
        "category": "SMARTPHONE",
        "brand": "APPLE"
    },
    "samsung": {
        "url_template": "https://www.leboncoin.fr/recherche?category=17&shippable=1&price=80-max&phone_brand=samsung&page={page}",
        "category": "SMARTPHONE",
        "brand": "SAMSUNG"
    },
    "playstation": {
        "url_template": "https://www.leboncoin.fr/recherche?category=43&shippable=1&video_game_type=console&console_brand=sony&page={page}", # Category 43 = Consoles
        "category": "CONSOLE",
        "brand": "SONY"
    },
    "xbox": {
        "url_template": "https://www.leboncoin.fr/recherche?category=43&shippable=1&price=60-max&video_game_type=console&console_brand=microsoft&console_model=xbox,xbox360,xboxone,xboxseriess,xboxseriesx&page={page}", # Category 43 = Consoles
        "category": "CONSOLE",
        "brand": "MICROSOFT"
    },
    "laptop": {
        "url_template": "https://www.leboncoin.fr/recherche?category=15&shippable=1&price=150-max&computer_type=laptop&page={page}", # Category 9 = Informatique
        "category": "ORDINATEUR",
        "brand": "laptop"
    }
}

def scrape_leboncoin_category(route_key, max_pages=3):
    config = SCRAPING_ROUTES.get(route_key.lower())
    if not config:
        print(f"❌ Aucune route configurée pour la clé : {route_key}")
        return

    print(f"🎯 [ROUTAGE LEBONCOIN] Extraction : {config['category']} | Marque : {config['brand']}")
    all_items = []
    
    # Initialisation de cloudscraper pour tenter d'atténuer Datadome
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    headers = {
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Referer": "https://www.google.com/",
        "Cache-Control": "max-age=0"
    }

    for page in range(1, max_pages + 1):
        url = config["url_template"].format(page=page)
        print(f"📡 Tentative Page {page} -> {url}")
        
        try:
            response = scraper.get(url, headers=headers, timeout=15)
            
            if response.status_code == 403:
                print("❌ Bloqué par le pare-feu Datadome (Code 403).")
                break
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ciblage du conteneur d'annonces LBC
            listings = soup.find_all('div', {'data-qa-id': 'aditem_container'})

            if not listings:
                print("🏁 Aucune annonce trouvée sur cette page. Fin de liste ou blocage furtif.")
                break

            page_results = 0
            for ad in listings:
                # 1. Extraction du Titre
                title_elem = ad.find('p', class_=lambda x: x and 'text-body-1' in x)
                
                # 2. Extraction du Prix 
                price_elem = ad.find('p', class_='sr-only')
                
                # 3. Extraction de l'URL
                link_elem = ad.find_parent('article').find_next('a', href=True) if ad.find_parent('article') else None

                if title_elem and price_elem:
                    title_text = title_elem.get_text(strip=True)
                    clean_price = price_elem.get_text(strip=True).replace("Prix: ", "")
                    url_product = "https://www.leboncoin.fr" + link_elem['href'] if link_elem else "N/A"
                    
                    all_items.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "LEBONCOIN",
                        "injected_category": config["category"], # Métadonnée unifiée pour Spark/dbt
                        "injected_brand": config["brand"],       # Métadonnée unifiée pour Spark/dbt
                        "title": title_text.upper(),
                        "price_raw": clean_price,
                        "etat": "OCCASION",
                        "url": url_product
                    })
                    page_results += 1

            print(f"✅ Page {page} : +{page_results} annonces collectées.")
            
            # Le Bon Coin demande des délais humains très lourds pour ne pas griller l'IP
            time.sleep(random.uniform(6, 12)) 

        except Exception as e:
            print(f"❌ Erreur sur la page {page}: {e}")
            break

    # Sauvegarde dans le volume partagé
    if all_items:
        df = pd.DataFrame(all_items)
        output_dir = "/opt/airflow/data/raw/shopping"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"lbc_{route_key.lower()}.csv"
        full_path = os.path.join(output_dir, filename)
        
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"✨ [SUCCÈS] {len(df)} lignes LeBonCoin poussées dans : {full_path}\n")
    else:
        print(f"❌ Aucune donnée générée pour la route LBC : {route_key}\n")

if __name__ == "__main__":
    input_str = sys.argv[1] if len(sys.argv) > 1 else "iphone,playstation,xbox,samsung,laptop"
    routes_to_run = [r.strip() for r in input_str.split(',')]
    
    for route in routes_to_run:
        # On reste à 3 pages max par run sur LBC pour limiter les risques de ban IP
        scrape_leboncoin_category(route, max_pages=3)
        
        sleep_between_queries = random.uniform(30, 60)
        print(f"💤 Pause de sécurité inter-routes : {int(sleep_between_queries)}s...")
        time.sleep(sleep_between_queries)