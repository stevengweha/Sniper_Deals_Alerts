import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import os
import sys
import cloudscraper
import random

def scrape_ebay(keyword, pages=1):
    all_items = []
    query_formatted = keyword.replace(' ', '+')
    
    # 1. initialisation du scraper avec impersonation Chrome sur Windows
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # 2. Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1"
    }

    print(f"🚀 Initialisation du scraping pour : {keyword}")

    # 3.  "chauffe" la session en allant sur la home page
    try:
        scraper.get("https://www.ebay.fr", headers=headers, timeout=10)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Warning initialisation session: {e}")

    for page in range(1, pages + 1):
        url = f"https://www.ebay.fr/sch/i.html?_nkw={query_formatted}&_pgn={page}"
        print(f"📡 Tentative Page {page}...")
        
        try:
            response = scraper.get(url, headers=headers, timeout=15)
            
            if response.status_code == 403:
                print(f"❌ Accès refusé (403) sur la page {page}. eBay bloque l'IP.")
                break 
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.select("li.s-card")
            

            

            page_results = 0
            for item in products:
                # Extraction du titre
                title_elem = item.select_one("span.su-styled-text") or \
                             item.select_one(".s-item__title")    or \
                             item.select_one(".s-card__title span su-styled-text")
                # Extraction du prix
                price_elem = item.select_one(".s-card__price")

                link_elem = item.select_one("a.s-card__link") or \
                            item.select_one("a.s-item__link")
                
                category_elem = item.select_one(".s-item__subtitle .secondary") or \
                                item.select_one(".su-styled-text.secondary") 
                
                if title_elem and price_elem:
                    # récupère le texte à l'intérieur
                    title_text = title_elem.text.strip()
                    price_text = price_elem.text.strip()

                    #  évite d'attraper les bannières d'annonces génériques d'eBay
                    if "vendre un objet" in title_text.lower() or not title_text:
                        continue
                    
                    # --- NETTOYAGE ET STANDARDISATION DE L'ÉTAT ---
                    etat_text = "Inconnu"
                    if category_elem:
                        # Nettoyage des pipes '|' et des espaces parasites 
                        raw_cat = category_elem.text.replace("|", "").strip()
                        
                        if "neuf" in raw_cat.lower():
                            etat_text = "Neuf"
                        elif "occasion" in raw_cat.lower():
                            etat_text = "Occasion"
                        elif "reconditionné" in raw_cat.lower() or "refurbished" in raw_cat.lower():
                            etat_text = "Reconditionné"
                        else:
                            etat_text = raw_cat.capitalize()
                    
                    all_items.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "keyword": keyword,
                        "title": title_text,
                        "price_raw": price_text,
                        "etat": etat_text,
                        "url": link_elem['href'] if link_elem and link_elem.has_attr('href') else "N/A"
                    })
                    page_results += 1
            
            print(f"✅ Page {page} : {page_results} produits extraits.")
            time.sleep(3) 

        except Exception as e:
            print(f"❌ Erreur critique page {page}: {e}")

    # 4. Sauvegarde robuste
    if all_items:
        df = pd.DataFrame(all_items)
        
        output_dir = "/opt/airflow/data/raw/shopping"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"ebay_search_{keyword.replace(' ', '_')}.csv"
        full_path = os.path.join(output_dir, filename)
        
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"\n✨ SUCCESS: {len(all_items)} lignes sauvegardées dans {full_path}")
    else:
        print("\n💀 ECHEC: Aucune donnée n'a pu être extraite.")
        sys.exit(0)

if __name__ == "__main__":
    input_str = sys.argv[1] if len(sys.argv) > 1 else "playstation"
    queries = [q.strip() for q in input_str.split(',')]
    
    for query in queries:
        scrape_ebay(query, pages=10)

        # Pause aléatoire entre chaque mot-clé pour éviter le bannissement
        sleep_between_queries = random.uniform(30, 60)
        print(f"💤 Pause de sécurité de {int(sleep_between_queries)}s...")
        time.sleep(sleep_between_queries)

    
   
