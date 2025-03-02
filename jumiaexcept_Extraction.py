import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class JumiaScraper:
    def __init__(self, category_name, base_url):
        self.category_name = category_name
        self.base_url = base_url
        self.base_directory = f"D:/bureau/grand projet/jumia/data/{category_name}"
        self.data_directory = os.path.join(self.base_directory, 'data')
        self.ensure_directories()

    def ensure_directories(self):
        """Créer les dossiers nécessaires s'ils n'existent pas"""
        os.makedirs(self.data_directory, exist_ok=True)
        print(f"Dossier vérifié/créé : {self.data_directory}")

    def get_page_url(self, page):
        """Générer l'URL pour une page spécifique"""
        return f"{self.base_url}?page={page}#catalog-listing" if page > 1 else self.base_url

    def get_total_pages(self, soup):
        """Obtenir le nombre total de pages disponibles"""
        pagination = soup.find_all('a', {'class': 'pg'})
        return max((int(p.text) for p in pagination if p.text.isdigit()), default=1)

    def extract_product_details(self, article):
        """Extraire les détails d'un produit"""
        product = article.find('a', class_='core')
        if not product:
            return None

        details = {
            'name': product.get('data-gtm-name', ''),
            'price': product.get('data-gtm-price', ''),
            'brand': product.get('data-gtm-brand', ''),
            'category': product.get('data-gtm-category', ''),
            'product_id': product.get('data-gtm-id', ''),
            'displayed_price': '',
            'image_url': '',
            'product_url': f"https://www.jumia.ma{product.get('href', '')}" if product.get('href', '').startswith('/') else product.get('href', '')
        }

        img_tag = product.find('img')
        if img_tag:
            details['image_url'] = img_tag.get('data-src', '') or img_tag.get('src', '')

        price_div = article.find('div', class_='prc')
        if price_div:
            details['displayed_price'] = price_div.text.strip()

        return details

    def scrape_products(self):
        """Scraper les produits et retourner une liste de dictionnaires"""
        products = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        print(f"Scraping de la catégorie : {self.category_name}")
        response = requests.get(self.get_page_url(1), headers=headers)

        if response.status_code != 200:
            print(f"Erreur d'accès à la page : {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        total_pages = self.get_total_pages(soup)
        print(f"Nombre total de pages : {total_pages}")

        for page in range(1, total_pages + 1):
            current_url = self.get_page_url(page)
            print(f"Traitement de la page {page}/{total_pages} : {current_url}")

            if page > 1:
                response = requests.get(current_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')

            product_articles = soup.find_all('article', class_='prd _fb col c-prd')
            print(f"Produits trouvés sur la page {page} : {len(product_articles)}")

            for article in product_articles:
                product_details = self.extract_product_details(article)
                if product_details:
                    product_details['page_number'] = page
                    product_details['page_url'] = current_url
                    products.append(product_details)

            time.sleep(2)  # Pause pour éviter le blocage

        return products

    def save_data(self, data):
        """Sauvegarder les données en CSV"""
        if not data:
            print("Aucune donnée à sauvegarder.")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"products_{self.category_name.lower()}_{timestamp}.csv"
        csv_path = os.path.join(self.data_directory, csv_filename)

        fieldnames = data[0].keys()
        with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Données sauvegardées : {csv_path}")
        return csv_path

    def run(self):
        """Exécuter l'extraction complète"""
        print(f"Lancement du scraping pour {self.category_name}...")
        products = self.scrape_products()
        if products:
            self.save_data(products)
            print(f"Scraping terminé avec succès ! {len(products)} produits extraits.")
        else:
            print("Aucun produit trouvé.")

if __name__ == "__main__":
    categories = {
        "Bricolage": "https://www.jumia.ma/mlp-bricolage-et-jardinage/",
        "Électroménager": "https://www.jumia.ma/mlp-electromenager/"
    }

    for category, url in categories.items():
        scraper = JumiaScraper(category, url)
        scraper.run()

