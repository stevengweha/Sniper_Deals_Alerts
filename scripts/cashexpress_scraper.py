import os
import sys
import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests
import random

def scrape_cashexpress_exact(keyword, target_count):
    print(f"🎯 [VRAIE STRUCTURE] Extraction via Cash Express pour : {keyword}")
    all_items = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    
    # On commence à la page 1 (offset 0)
    current_page = 1
    
    with requests.Session(impersonate="chrome120") as session:
        while len(all_items) < target_count:
            # Calcul exact de l'offset basé sur : (Page - 1) * 16
            offset = (current_page - 1) * 16
            url = f"https://www.cashexpress.fr/produits-occasions/page,{offset}.html?recherche={keyword}"
            
            print(f"📡 Requête Page {current_page} (Offset {offset}) -> {url}")
            
            try:
                response = session.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    print(f"❌ Erreur serveur ou fin de catalogue ({response.status_code})")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ciblage strict du conteneur 
                product_cards = soup.find_all("div", class_="item_produit_magasin")
                
                if not product_cards:
                    print("🏁 Aucun produit trouvé sur cette page. Fin de l'index.")
                    break
                
                items_found_this_page = 0
                for card in product_cards:
                    if len(all_items) >= target_count:
                        break
                    
                    # 1. Extraction du Titre et de l'URL via le H3 > A du snippet
                    h3_element = card.find("h3")
                    if not h3_element:
                        continue
                        
                    a_element = h3_element.find("a")
                    if not a_element:
                        continue
                        
                    title = a_element.text.strip().upper()
                    href = a_element.get("href", "")
                    url_product = f"https://www.cashexpress.fr{href}"
                    
                    # Filtre de sécurité pour éviter les accessoires
                    if any(p in title.lower() for p in ["telecommande", "support", "cable", "fixation"]):
                        continue
                    
                    # 2. Extraction du Prix 
                    price_element = card.find("span", class_="prix")
                    if not price_element:
                        continue
                    price_raw = price_element.text.strip() # Récupère "69.99 €"
                    
                    # 3. État sémantique (Le site étant 100% occasion, on garde "Occasion")
                    etat = "Occasion"

                    all_items.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "keyword": keyword,
                        "title": title,
                        "price_raw": price_raw,
                        "etat": etat,
                        "url": url_product
                    })
                    items_found_this_page += 1
                
                print(f"📊 Page {current_page} complétée : +{items_found_this_page} lignes (Total : {len(all_items)}/{target_count})")
                
                if items_found_this_page == 0:
                    print("🏁 Les structures sont vides. Arrêt.")
                    break
                    
                current_page += 1
                time.sleep(1) 
                
            except Exception as e:
                print(f"💥 Incident de parsing sur la page {current_page} : {e}")
                break

    # Écriture finale dans le volume d'ingestion dbt / Airflow
    if all_items:
        df = pd.DataFrame(all_items)
        output_dir = "/opt/airflow/data/raw/shopping"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"cashexpress_{keyword.lower()}.csv"
        full_path = os.path.join(output_dir, filename)
        
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"✨ [SUCCÈS] {len(df)} lignes réelles générées dans : {full_path}")
        
    else:
        print("❌ Aucune donnée n'a pu être extraite.")
        sys.exit(0)

if __name__ == "__main__":
    input_str = sys.argv[1] if len(sys.argv) > 1 else "playstation"
    queries = [q.strip() for q in input_str.split(',')]
    
    for query in queries:
        scrape_cashexpress_exact(query, target_count=500)
        # Pause aléatoire entre chaque mot-clé pour éviter le bannissement
        sleep_between_queries = random.uniform(30, 60)
        print(f"💤 Pause de sécurité de {int(sleep_between_queries)}s...")
        time.sleep(sleep_between_queries)