import json
import csv
from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime
import time

class JumiaDataExtractor:
    def __init__(self, base_directory):
        self.base_directory = base_directory
        self.data_directory = os.path.join(base_directory, 'data')
        self.ensure_directories()
        
    def ensure_directories(self):
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)

    def clean_url(self, url):
        """Nettoyer l'URL pour la pagination"""
        base_url = url.split('?')[0]  # Retirer les paramètres
        base_url = base_url.split('#')[0]  # Retirer le #catalog-listing
        return base_url.rstrip('/')

    def get_page_url(self, base_url, page):
        """Générer l'URL pour une page spécifique"""
        clean_base = self.clean_url(base_url)
        if page == 1:
            return f"{clean_base}/"
        return f"{clean_base}/?page={page}#catalog-listing"

    def extract_product_details(self, html):
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
        pagination = soup.find_all('a', {'class': 'pg'})
        if pagination:
            try:
                # Prendre le dernier numéro de page
                last_page = max([int(p.text) for p in pagination if p.text.isdigit()])
                return last_page
            except (ValueError, IndexError):
                return 1
        return 1

    def save_data(self, data, filename):
        """Sauvegarder les données en CSV avec timestamp"""
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
        """Scraper une catégorie spécifique avec toutes ses pages"""
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
            
            # Obtenir le nombre total de pages
            first_page_url = self.get_page_url(base_url, 1)
            response = requests.get(first_page_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                total_pages = self.get_total_pages(soup)
                print(f"Nombre total de pages: {total_pages}")
                
                # Parcourir chaque page
                for page in range(1, total_pages + 1):
                    current_url = self.get_page_url(base_url, page)
                    print(f"Traitement de la page {page}/{total_pages}")
                    
                    if page > 1:
                        response = requests.get(current_url, headers=headers)
                        soup = BeautifulSoup(response.text, 'html.parser')
                    
                    product_articles = soup.find_all('article', class_='prd _fb col c-prd')
                    print(f"Nombre de produits trouvés sur la page {page}: {len(product_articles)}")
                    
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
                    
                    # Pause entre les pages pour éviter d'être bloqué
                    if page < total_pages:
                        time.sleep(2)
            
            else:
                print(f"Erreur lors de l'accès à l'URL: {response.status_code}")
                
        except Exception as e:
            print(f"Erreur lors du traitement de {base_url}: {str(e)}")
        
        return products

    def process_all_categories(self):
        """Traiter toutes les catégories du fichier CSV"""
        csv_path = os.path.join(self.base_directory, 'jumia_data/subcategories/processed_subcategories.csv')
        all_products = []
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for category in reader:
                products = self.scrape_category(category)
                all_products.extend(products)
                
                # Sauvegarder les produits de cette catégorie
                if products:
                    category_filename = f"products_{category['subcategory']}_{category['text'].replace(' ', '_')}"
                    self.save_data(products, category_filename)
        
        # Sauvegarder tous les produits dans un seul fichier
        if all_products:
            self.save_data(all_products, 'all_products')
        
        return all_products

def main():
    base_dir = "D:/bureau/grand projet/jumia/telefone"
    extractor = JumiaDataExtractor(base_dir)
    extractor.process_all_categories()

if __name__ == "__main__":
    main()