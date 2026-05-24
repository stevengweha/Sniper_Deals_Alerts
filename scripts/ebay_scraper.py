import os
import sys
import time
import pandas as pd
from datetime import datetime
import cloudscraper
from bs4 import BeautifulSoup
import random

# CONFIGURATION DES ROUTES SUR MESURE (URLs filtrées avec tes paramètres d'origine)
# LH_ItemCondition=3000 (D'occasion) | LH_BIN=1 (Achat immédiat / Sans enchères)
SCRAPING_ROUTES = {
    "iphone": {
        "url_template": "https://www.ebay.fr/sch/i.html?_nkw=iphone&_sacat=15032&_from=R40&LH_ItemCondition=3000&LH_PrefLoc=1&LH_BIN=1&_pgn={page}",
        "category": "SMARTPHONE",
        "brand": "APPLE"
    },
    "samsung": {
        "url_template": "https://www.ebay.fr/sch/i.html?_nkw=samsung&_sacat=0&_from=R40&_fsrp=1&LH_ItemCondition=2000%7C2010%7C3000%7C2020%7C2030%7C1500&rt=nc&_udlo=99&_pgn={page}",
        "category": "SMARTPHONE",
        "brand": "SAMSUNG"
    },
    "playstation": {
        "url_template": "https://www.ebay.fr/sch/i.html?_nkw=console+sony&_sacat=0&_from=R40&LH_TitleDesc=0&_fsrp=1&_udlo=65&rt=nc&_pgn={page}",
        "category": "CONSOLE",
        "brand": "SONY"
    },
    "xbox": {
        "url_template": "https://www.ebay.fr/sch/i.html?_nkw=xbox&_sacat=0&_from=R40&_trksid=p2334524.m570.l1313&_fsrp=1&_udlo=65&rt=nc&_pgn={page}",
        "category": "CONSOLE",
        "brand": "MICROSOFT"
    },
    "laptop": {
        "url_template": "https://www.ebay.fr/sch/i.html?_nkw=laptop&_sacat=0&_from=R40&_trksid=p2334524.m570.l1313&_fsrp=1&_udlo=65&rt=nc&_pgn={page}",
        "category": "ORDINATEUR",
        "brand": "laptop"
    }
}

def scrape_ebay_category(route_key, max_pages=5):
    config = SCRAPING_ROUTES.get(route_key.lower())
    if not config:
        print(f"❌ Aucune route configurée pour la clé : {route_key}")
        return

    print(f"🎯 [ROUTAGE EBAY] Extraction : {config['category']} | Marque : {config['brand']}")
    all_items = []
    
    # 1. Initialisation de cloudscraper (Impersonation pour bypass Cloudflare)
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1"
    }

    # 2. Chauffe de la session
    try:
        scraper.get("https://www.ebay.fr", headers=headers, timeout=10)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Début de session instable : {e}")

    # 3. Boucle de pagination
    for page in range(1, max_pages + 1):
        url = config["url_template"].format(page=page)
        print(f"📡 Requête Page {page} -> {url}")
        
        try:
            response = scraper.get(url, headers=headers, timeout=15)
            
            if response.status_code == 403:
                print(f"❌ Accès refusé (403). L'IP est temporairement bloquée par eBay.")
                break
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sélecteur eBay standard pour les cartes d'articles
            products = soup.select("li.s-item") or soup.select("li.s-card")
            
            if not products:
                print("🏁 Aucun produit détecté. Fin de liste ou structure modifiée.")
                break
            
            page_results = 0
            for item in products:
                # Extraction Titre
                title_elem = item.select_one(".s-item__title") or item.select_one("span.su-styled-text")
                # Extraction Prix
                price_elem = item.select_one(".s-item__price") or item.select_one(".s-card__price")
                # Extraction Lien
                link_elem = item.select_one("a.s-item__link") or item.select_one("a.s-card__link")
                
                if title_elem and price_elem:
                    title_text = title_elem.text.strip()
                    price_text = price_elem.text.strip()
                    
                    # Bypass des bannières publicitaires parasites d'eBay
                    if "vendre un objet" in title_text.lower() or not title_text:
                        continue
                        
                    # Récupération de l'URL propre
                    url_product = link_elem['href'].split('?')[0] if link_elem and link_elem.has_attr('href') else "N/A"
                    
                    all_items.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "EBAY",
                        "injected_category": config["category"],  # VALEUR ET CLASSIFICATION SPARK DIRECTE
                        "injected_brand": config["brand"],        # VALEUR ET CLASSIFICATION SPARK DIRECTE
                        "title": title_text.upper(),
                        "price_raw": price_text,
                        "etat": "OCCASION",  # Garanti à 100% par ton paramètre d'URL LH_ItemCondition=3000
                        "url": url_product
                    })
                    page_results += 1
            
            print(f"✅ Page {page} terminée : +{page_results} annonces capturées.")
            
            if page_results == 0:
                break
                
            # Pause humaine pour éviter le trigger anti-bot
            time.sleep(random.uniform(3, 6))

        except Exception as e:
            print(f"❌ Erreur sur la page {page}: {e}")
            break

    # 4. Sauvegarde dans le volume de stockage partagé d'Airflow
    if all_items:
        df = pd.DataFrame(all_items)
        output_dir = "/opt/airflow/data/raw/shopping"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"ebay_{route_key.lower()}.csv"
        full_path = os.path.join(output_dir, filename)
        
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"✨ [SUCCÈS] {len(df)} lignes eBay déversées dans : {full_path}\n")
    else:
        print(f"❌ Aucune donnée générée pour la route : {route_key}\n")

if __name__ == "__main__":
    input_str = sys.argv[1] if len(sys.argv) > 1 else "iphone,playstation,xbox,samsung,laptop"
    routes_to_run = [r.strip() for r in input_str.split(',')]
    
    for route in routes_to_run:
        # On limite par défaut à 5 pages pour les tests d'ingestion (environ 250-300 articles)
        scrape_ebay_category(route, max_pages=5)
        
        # Anti-ban cooldown entre les différentes catégories
        sleep_time = random.uniform(20, 40)
        print(f"💤 Latence de sécurité inter-routes : {int(sleep_time)}s...")
        time.sleep(sleep_time)