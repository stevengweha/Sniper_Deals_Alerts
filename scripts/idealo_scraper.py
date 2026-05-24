import os
import sys
import time
import pandas as pd
from datetime import datetime
import cloudscraper
from bs4 import BeautifulSoup
import random
import re

# CONFIGURATION DES ROUTES CHIRURGICALES IDEALO
# L'offset d'Idealo fonctionne par pas de 15 articles (-15, -30, -45...) après l'ID de la catégorie
SCRAPING_ROUTES = {
    "iphone": {
        "url_template": "https://www.idealo.fr/cat/19116F1827923{offset}/smartphones.html?sortKey=listedSince",
        "category": "SMARTPHONE",
        "brand": "APPLE"
    },
    "samsung": {
        "url_template": "https://www.idealo.fr/cat/19116F1824568{offset}/smartphones.html?sortKey=listedSince",
        "category": "SMARTPHONE",
        "brand": "SAMSUNG"
    },
    "playstation": {
        "url_template": "https://www.idealo.fr/cat/3189F3767161{offset}/consoles-de-jeux.html?sortKey=listedSince",
        "category": "CONSOLE",
        "brand": "SONY"
    },
    "xbox": {
        "url_template": "https://www.idealo.fr/cat/3189F4390841{offset}/consoles-de-jeux.html?sortKey=listedSince",
        "category": "CONSOLE",
        "brand": "MICROSOFT"
    },
    "laptop": {
        "url_template": "https://www.idealo.fr/cat/3751I16{offset}/ordinateurs-portables.html?sortKey=listedSince",
        "category": "ORDINATEUR",
        "brand": "laptop"
    }
}

def clean_idealo_price(price_text):
    """Extrait le prix numérique du texte (ex: 'à partir de615,00 €' -> '615.00')"""
    if not price_text:
        return "0.0"
    # Nettoie les espaces insécables et isole les chiffres et la virgule
    cleaned = re.sub(r'[^\d,]', '', price_text).replace(',', '.')
    return cleaned

def scrape_idealo_category(route_key, max_pages=3):
    config = SCRAPING_ROUTES.get(route_key.lower())
    if not config:
        print(f"❌ Aucune route configurée pour la clé : {route_key}")
        return

    print(f"🎯 [ROUTAGE IDEALO] Extraction : {config['category']} | Marque : {config['brand']}")
    all_items = []
    
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
        # Calcul du pattern d'offset d'Idealo (-15, -30, etc.)
        offset_str = "" if page == 1 else f"-{(page - 1) * 15}"
        url = config["url_template"].format(offset=offset_str)
        
        print(f"📡 Tentative Page {page} -> {url}")
        
        try:
            response = scraper.get(url, headers=headers, timeout=15)
            
            if response.status_code == 403:
                print("❌ Bloqué par le pare-feu Idealo (Code 403 / Cloudflare).")
                break
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ciblage du conteneur d'un bloc produit basé sur ton HTML exemple
            listings = soup.find_all('div', class_=lambda x: x and 'sr-resultItemTile_' in x)

            if not listings:
                print("🏁 Aucune annonce trouvée sur cette page. Fin de liste ou blocage furtif.")
                break

            page_results = 0
            for ad in listings:
                # 1. Extraction du Titre
                title_elem = ad.find('div', class_=lambda x: x and 'productSummary__title' in x)
                
                # 2. Extraction du Prix (contient le préfixe et le prix)
                price_elem = ad.find('div', class_=lambda x: x and 'detailedPriceInfo__price' in x)
                
                # 3. Extraction de l'URL du comparatif
                link_elem = ad.find('a', href=True)
                
                # 4. Extraction de l'ID unique produit fourni par Idealo dans le bouton de favoris
                wishlist_span = ad.find('span', class_=lambda x: x and 'sr-wishlistHeart__button' in x)

                if title_elem and price_elem:
                    title_text = title_elem.get_text(strip=True)
                    price_raw = clean_idealo_price(price_elem.get_text(strip=True))
                    url_product = link_elem['href'] if link_elem else "N/A"
                    
                    # Récupération de l'ID unique via le JSON du data-attribute si dispo, sinon via l'URL
                    if wishlist_span and wishlist_span.has_attr('data-wishlist-heart'):
                        import json
                        try:
                            meta_js = json.loads(wishlist_span['data-wishlist-heart'])
                            product_id = meta_js.get('id', 'N/A')
                        except:
                            product_id = url_product.split('/')[-1].replace('.html', '')
                    else:
                        product_id = url_product.split('/')[-1].replace('.html', '')

                    all_items.append({
                        "product_id": product_id,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "IDEALO",
                        "injected_category": config["category"], 
                        "injected_brand": config["brand"],       
                        "title": title_text.upper(),
                        "price_raw": price_raw,
                        "etat": "NEUF", # Par défaut sur Idealo (Comparateur de prix du neuf)
                        "url": url_product
                    })
                    page_results += 1

            print(f"✅ Page {page} : +{page_results} articles collectés.")
            
            # Délais de sécurité humains pour éviter le ban IP
            time.sleep(random.uniform(6, 12)) 

        except Exception as e:
            print(f"❌ Erreur sur la page {page}: {e}")
            break

    # Sauvegarde dans ton volume partagé Airflow
    if all_items:
        df = pd.DataFrame(all_items)
        output_dir = "/opt/airflow/data/raw/shopping"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"idealo_{route_key.lower()}.csv"
        full_path = os.path.join(output_dir, filename)
        
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"✨ [SUCCÈS] {len(df)} lignes Idealo poussées dans : {full_path}\n")
    else:
        print(f"❌ Aucune donnée générée pour la route Idealo : {route_key}\n")

if __name__ == "__main__":
    input_str = sys.argv[1] if len(sys.argv) > 1 else "iphone,samsung,playstation,xbox,laptop"
    routes_to_run = [r.strip() for r in input_str.split(',')]
    
    for route in routes_to_run:
        scrape_idealo_category(route, max_pages=3)
        
        sleep_between_queries = random.uniform(30, 60)
        print(f"💤 Pause de sécurité inter-routes : {int(sleep_between_queries)}s...")
        time.sleep(sleep_between_queries)