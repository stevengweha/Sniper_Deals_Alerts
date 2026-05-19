import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
import random
import sys

def scrape_amazon(keyword, pages=1):
    all_items = []
    # On initialise un scraper avec une empreinte navigateur fixe
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    print(f"🚀 Lancement du mode 'Forçage' pour : {keyword}")

    for page in range(1, pages + 1):
        url = f"https://www.amazon.fr/s?k={keyword.replace(' ', '+')}&page={page}"
        
        # Headers haute fidélité pour éviter le code 202
        headers = {
            "authority": "www.amazon.fr",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "fr-FR,fr;q=0.9",
            "device-memory": "8",
            "downlink": "10",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        try:
            # ÉTAPE CRUCIALE : On attend un peu avant la requête pour casser le rythme Airflow
            time.sleep(random.uniform(2, 5))
            
            response = scraper.get(url, headers=headers, timeout=30)
            
            # Si on reçoit encore un 202, on fait une petite boucle de retry immédiat
            if response.status_code == 202:
                print("⚠️ Code 202 reçu. Tentative de rafraîchissement après 5s...")
                time.sleep(5)
                response = scraper.get(url, headers=headers, timeout=30)

            print(f"📡 Page {page} : Status {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sélecteur d'image_d90a7c.png
            products = soup.find_all('div', {'data-component-type': 's-search-result'})

            for product in products:
                # Utilisation des data-cy de l'image image_d90a7c.png
                title_container = product.find('div', {'data-cy': 'title-recipe'})
                title_node = title_container.find('h2') if title_container else None
                
                price_container = product.find('div', {'data-cy': 'price-recipe'})
                # On cherche le prix spécifique dans les spans a-offscreen
                price_node = price_container.find('span', class_='a-offscreen') if price_container else None
                
                asin = product.get('data-asin')

                if title_node and price_node:
                    all_items.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "amazon",
                        "asin": asin if asin else "N/A",
                        "keyword": keyword,
                        "title": title_node.get_text(strip=True),
                        "price_raw": price_node.get_text(strip=True).replace('\xa0', ' ')
                    })

            print(f"✅ Page {page} : {len(all_items)} produits extraits.")
            time.sleep(random.uniform(5, 15))

        except Exception as e:
            print(f"❌ Erreur : {e}")

    # Sauvegarde finale
    if all_items:
        output_dir = "/opt/spark/data/raw/shopping"
        os.makedirs(output_dir, exist_ok=True)
        df = pd.DataFrame(all_items)
        df.to_csv(f"{output_dir}/amazon_{keyword}.csv", index=False)
        print(f"✨ Terminé avec {len(all_items)} lignes.")
    else:
        # On affiche un snippet du HTML pour débugger dans Airflow si 0 résultats
        print("💀 Échec. Vérification du contenu HTML...")
        if 'response' in locals():
            print(f"Extrait du HTML : {response.text[:500]}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "tele"
    scrape_amazon(query, pages=1)