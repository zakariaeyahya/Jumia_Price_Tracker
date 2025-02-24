import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class JumiaElectromenagerExtractor:
    def __init__(self):
        self.base_url = "https://www.jumia.ma/mlp-electromenager/"
        self.base_directory = "D:/bureau/grand projet/jumia/electromenager"
        self.data_directory = os.path.join(self.base_directory, 'data')
        self.ensure_directories()

    def ensure_directories(self):
        """Créer les dossiers nécessaires s'ils n'existent pas"""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            print(f"Dossier créé: {self.data_directory}")

    def clean_url(self, url):
        """Nettoyer l'URL pour la pagination"""
        return url.split('?')[0].split('#')[0].rstrip('/')

    def get_page_url(self, page):
        """Générer l'URL pour une page spécifique"""
        if page == 1:
            return f"{self.base_url}"
        return f"{self.base_url}?page={page}#catalog-listing"

    def get_total_pages(self, soup):
        """Obtenir le nombre total de pages"""
        pagination = soup.find_all('a', {'class': 'pg'})
        if pagination:
            try:
                return max(int(p.text) for p in pagination if p.text.isdigit())
            except (ValueError, IndexError):
                return 1
        return 1

    def extract_product_details(self, article):
        """Extraire les détails d'un produit"""
        product = article.find('a', class_='core')
        if product:
            details = {
                'name': product.get('data-gtm-name', ''),
                'price': product.get('data-gtm-price', ''),
                'brand': product.get('data-gtm-brand', ''),
                'category': product.get('data-gtm-category', ''),
                'product_id': product.get('data-gtm-id', ''),
                'displayed_price': '',
                'image_url': '',
                'product_url': "https://www.jumia.ma" + product.get('href', '') if product.get('href', '').startswith('/') else product.get('href', '')
            }

            img_tag = product.find('img')
            if img_tag:
                details['image_url'] = img_tag.get('data-src', '') or img_tag.get('src', '')

            price_div = article.find('div', class_='prc')
            if price_div:
                details['displayed_price'] = price_div.text.strip()

            return details
        return None

    def scrape_products(self):
        """Scraper tous les produits de la catégorie électroménager"""
        products = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        print(f"Scraping de la page principale: {self.base_url}")
        response = requests.get(self.get_page_url(1), headers=headers)

        if response.status_code != 200:
            print(f"Erreur lors de l'accès à la page: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        total_pages = self.get_total_pages(soup)
        print(f"Nombre total de pages: {total_pages}")

        for page in range(1, total_pages + 1):
            current_url = self.get_page_url(page)
            print(f"Traitement de la page {page}/{total_pages}: {current_url}")

            if page > 1:
                response = requests.get(current_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')

            product_articles = soup.find_all('article', class_='prd _fb col c-prd')
            print(f"Produits trouvés sur la page {page}: {len(product_articles)}")

            for article in product_articles:
                product_details = self.extract_product_details(article)
                if product_details:
                    product_details['page_number'] = page
                    product_details['page_url'] = current_url
                    products.append(product_details)

            if page < total_pages:
                time.sleep(2)  # Pause pour éviter le blocage

        return products

    def save_data(self, data):
        """Sauvegarder les données en CSV"""
        if not data:
            print("Aucune donnée à sauvegarder.")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"products_electromenager_{timestamp}.csv"
        csv_path = os.path.join(self.data_directory, csv_filename)

        fieldnames = data[0].keys()
        with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Données sauvegardées dans: {csv_path}")
        return csv_path

    def run(self):
        """Exécuter l'extraction complète"""
        print("Démarrage du scraping...")
        products = self.scrape_products()
        if products:
            self.save_data(products)
            print(f"Scraping terminé avec succès! {len(products)} produits extraits.")
        else:
            print("Aucun produit trouvé.")

if __name__ == "__main__":
    extractor = JumiaElectromenagerExtractor()
    extractor.run()
