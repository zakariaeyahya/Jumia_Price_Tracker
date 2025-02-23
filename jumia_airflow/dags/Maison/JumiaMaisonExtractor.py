import json
import csv
from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime
import time

class JumiaElectronicsExtractor:
    def __init__(self):
        self.base_directory = "D:/bureau/grand projet/jumia/Maison/data"
        self.json_directory = self.base_directory
        self.data_directory = os.path.join(self.base_directory, 'data')
        self.data_directory = os.path.join(self.base_directory, 'data')
        self.categories_file = os.path.join(self.json_directory, 'categories', 'all_categories.json')
        self.subcategories_file = os.path.join(self.json_directory, 'subcategories', 'processed_subcategories.csv')
        
        print(f"Base directory: {self.base_directory}")
        print(f"JSON directory: {self.json_directory}")
        print(f"Data directory: {self.data_directory}")
        print(f"Categories file: {self.categories_file}")
        
        self.ensure_directories()

    def ensure_directories(self):
        """Créer les dossiers nécessaires s'ils n'existent pas"""
        for dir_path in [self.data_directory, os.path.dirname(self.subcategories_file)]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Dossier créé: {dir_path}")

    def convert_json_to_csv(self):
        """Convertir les données JSON en CSV"""
        print(f"Recherche du fichier JSON: {self.categories_file}")

        if not os.path.exists(self.categories_file):
            print(f"Fichier JSON non trouvé: {self.categories_file}")
            print("Assurez-vous d'avoir d'abord exécuté le scraper de catégories")
            return None

        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                categories = json.load(f)
            print(f"Fichier JSON lu avec succès. {len(categories)} catégories trouvées.")

            csv_data = []
            for category in categories:
                base_info = {
                    'text': category['category'],
                    'href': category['url'],
                }

                for sub in category.get('sub_elements', []):
                    sub_data = base_info.copy()
                    sub_data['subcategory'] = sub['text'].lower().replace(' ', '_')
                    sub_data['href'] = "https://www.jumia.ma" + sub['href'] if sub['href'].startswith('/') else sub['href']
                    csv_data.append(sub_data)

            print(f"Préparation de {len(csv_data)} sous-catégories pour le CSV")

            os.makedirs(os.path.dirname(self.subcategories_file), exist_ok=True)
            with open(self.subcategories_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['text', 'href', 'subcategory'])
                writer.writeheader()
                writer.writerows(csv_data)

            print(f"CSV créé avec succès: {self.subcategories_file}")
            return self.subcategories_file

        except Exception as e:
            print(f"Erreur lors de la conversion JSON vers CSV: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

    def clean_url(self, url):
        """Nettoyer l'URL pour la pagination"""
        base_url = url.split('?')[0]
        base_url = base_url.split('#')[0]
        return base_url.rstrip('/')

    def get_page_url(self, base_url, page):
        """Générer l'URL pour une page spécifique"""
        clean_base = self.clean_url(base_url)
        if page == 1:
            return f"{clean_base}/"
        return f"{clean_base}/?page={page}#catalog-listing"

    def extract_product_details(self, html):
        """Extraire les détails d'un produit"""
        soup = BeautifulSoup(html, 'html.parser')
        product = soup.find('a', class_='core')

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

            price_div = product.find('div', class_='prc')
            if price_div:
                details['displayed_price'] = price_div.text.strip()

            return details
        return None

    def get_total_pages(self, soup):
        """Obtenir le nombre total de pages"""
        pagination = soup.find_all('a', {'class': 'pg'})
        if pagination:
            try:
                last_page = max([int(p.text) for p in pagination if p.text.isdigit()])
                return last_page
            except (ValueError, IndexError):
                return 1
        return 1

    def save_data(self, data, filename):
        """Sauvegarder les données en CSV"""
        if not data:
            print(f"Pas de données à sauvegarder pour {filename}")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{filename}_{timestamp}.csv"
        csv_path = os.path.join(self.data_directory, csv_filename)

        fieldnames = data[0].keys()
        with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Données sauvegardées dans: {csv_path}")
        return csv_path

    def scrape_category(self, category_info):
        """Scraper une catégorie spécifique"""
        base_url = category_info['href']
        category_name = category_info['text']
        subcategory = category_info['subcategory']
        products = []

        print(f"\nTraitement de la catégorie: {category_name}")
        print(f"URL de base: {base_url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            first_page_url = self.get_page_url(base_url, 1)
            response = requests.get(first_page_url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                total_pages = self.get_total_pages(soup)
                print(f"Nombre total de pages: {total_pages}")

                for page in range(1, total_pages + 1):
                    current_url = self.get_page_url(base_url, page)
                    print(f"Traitement de la page {page}/{total_pages}")

                    if page > 1:
                        response = requests.get(current_url, headers=headers)
                        soup = BeautifulSoup(response.text, 'html.parser')

                    product_articles = soup.find_all('article', class_='prd _fb col c-prd')
                    print(f"Produits trouvés sur la page {page}: {len(product_articles)}")

                    for article in product_articles:
                        product_details = self.extract_product_details(str(article))
                        if product_details:
                            product_details.update({
                                'subcategory': subcategory,
                                'category_name': category_name,
                                'page_number': page,
                                'page_url': current_url
                            })
                            products.append(product_details)

                    if page < total_pages:
                        time.sleep(2)

            else:
                print(f"Erreur lors de l'accès à l'URL: {response.status_code}")

        except Exception as e:
            print(f"Erreur lors du traitement de {base_url}: {str(e)}")

        return products

    def process_all_categories(self):
        """Traiter toutes les catégories depuis le fichier CSV"""
        all_products = []

        try:
            with open(self.subcategories_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for category in reader:
                    products = self.scrape_category(category)
                    all_products.extend(products)

                    if products:
                        category_filename = f"products_{category['subcategory']}_{category['text'].replace(' ', '_')}"
                        self.save_data(products, category_filename)

            if all_products:
                self.save_data(all_products, 'all_products')

            return all_products

        except Exception as e:
            print(f"Erreur lors du traitement des catégories: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

def main():
    print("Initialisation de l'extracteur de données Jumia Electronics...")
    extractor = JumiaElectronicsExtractor()
    
    print("\nÉtape 1: Conversion des données JSON en CSV...")
    csv_path = extractor.convert_json_to_csv()
    
    if csv_path and os.path.exists(csv_path):
        print("\nÉtape 2: Début du scraping des produits...")
        products = extractor.process_all_categories()
        if products:
            print(f"\nScraping terminé avec succès! {len(products)} produits extraits.")
        else:
            print("\nAucun produit n'a été extrait.")
    else:
        print("\nImpossible de continuer sans le fichier CSV des catégories")

if __name__ == "__main__":
    main()