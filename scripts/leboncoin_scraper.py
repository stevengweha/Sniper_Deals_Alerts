import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import sys
import time
import random

def scrape_leboncoin(keyword, pages=1):
    all_items = []
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    # Headers additionnels pour plus de réalisme
    headers = {
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Referer": "https://www.google.com/"
    }
    query_formatted = keyword.replace(' ', '+')

    print(f"🚀 Scraping Le Bon Coin pour : {keyword}")

    for page in range(1, pages + 1):
        url = f"https://www.leboncoin.fr/recherche?text={query_formatted}&page={page}"
        print(f"📡 Tentative Page {page}...")
        
        try:
            response = scraper.get(url, headers=headers, timeout=15)
            
            if response.status_code == 403:
                print("❌ Bloqué par Datadome (403).")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            #  cible le conteneur principal 
            listings = soup.find_all('div', {'data-qa-id': 'aditem_container'})

            for ad in listings:
                # 1. Extraction du Titre 
                title_elem = ad.find('p', class_=lambda x: x and 'text-body-1' in x)
                
                # 2. Extraction du Prix 
                price_elem = ad.find('p', class_='sr-only')
                
                # 3. Extraction de l'URL
                link_elem = ad.find_parent('article').find_next('a', href=True) if ad.find_parent('article') else None

                if title_elem and price_elem:
                    # Nettoyage du prix (ex: "Prix: 997 500 €" -> "997 500 €")
                    clean_price = price_elem.get_text(strip=True).replace("Prix: ", "")
                    
                    all_items.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "leboncoin",
                        "keyword": keyword,
                        "title": title_elem.get_text(strip=True),
                        "price_raw": clean_price,
                        "etat": "Occasion",
                        "url": "https://www.leboncoin.fr" + link_elem['href'] if link_elem else "N/A"
                    })

            print(f"✅ Page {page} : {len(listings)} produits trouvés.")
            time.sleep(random.uniform(5, 12)) 

        except Exception as e:
            print(f"❌ Erreur : {e}")

    # Sauvegarde
    if all_items:
        output_dir = "/opt/airflow/data/raw/shopping"
        os.makedirs(output_dir, exist_ok=True)

        df = pd.DataFrame(all_items)
        filename = f"lbc_search_{keyword}.csv"
        df.to_csv(os.path.join(output_dir, filename), index=False)
        print(f"✨ Terminé ! {len(all_items)} produits sauvegardés dans {filename}")
    else:
        print("💀 Aucune donnée extraite. Vérifiez si le sélecteur 'aditem_container' est toujours présent.")
        sys.exit(0)
        
if __name__ == "__main__":
    input_str = sys.argv[1] if len(sys.argv) > 1 else "playstation"
    queries = [q.strip() for q in input_str.split(',')]
    
    for query in queries:
        scrape_leboncoin(query, pages=20)
        # Pause aléatoire entre chaque mot-clé pour éviter le bannissement
        sleep_between_queries = random.uniform(30, 60)
        print(f"💤 Pause de sécurité de {int(sleep_between_queries)}s...")
        time.sleep(sleep_between_queries)
    