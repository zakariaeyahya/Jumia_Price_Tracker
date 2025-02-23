import json
import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class JumiaAccInfoExtractor:
    def __init__(self):
        self.base_directory = "D:/bureau/grand projet/jumia/acc_info/data"
        self.json_directory = self.base_directory
        self.data_directory = os.path.join(self.base_directory, 'data')
        self.categories_file = os.path.join(self.json_directory, 'categories', 'all_categories.json')
        self.subcategories_file = os.path.join(self.json_directory, 'subcategories', 'processed_subcategories.csv')
        self.base_url = "https://www.jumia.ma"
        
        print(f"Base directory: {self.base_directory}")
        print(f"JSON directory: {self.json_directory}")
        print(f"Data directory: {self.data_directory}")
        print(f"Categories file: {self.categories_file}")
        
        self.ensure_directories()

    def ensure_directories(self):
        for dir_path in [self.data_directory, os.path.dirname(self.subcategories_file)]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Dossier créé: {dir_path}")

    def convert_json_to_csv(self):
        if not os.path.exists(self.categories_file):
            print(f"Fichier JSON non trouvé: {self.categories_file}")
            return None

        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                categories = json.load(f)

            csv_data = []
            for category in categories:
                base_info = {
                    'text': category['category'],
                    'href': category['url'],
                }
                for sub in category.get('sub_elements', []):
                    sub_data = base_info.copy()
                    sub_data['subcategory'] = sub['text'].lower().replace(' ', '_')
                    sub_data['href'] = self.base_url + sub['href'] if sub['href'].startswith('/') else sub['href']
                    csv_data.append(sub_data)

            os.makedirs(os.path.dirname(self.subcategories_file), exist_ok=True)
            with open(self.subcategories_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['text', 'href', 'subcategory'])
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"CSV créé avec succès: {self.subcategories_file}")
            return self.subcategories_file
        except Exception as e:
            print(f"Erreur: {str(e)}")
            return None

    def get_total_pages(self, soup):
        pagination = soup.find_all('a', {'class': 'pg'})
        if pagination:
            try:
                return max([int(p.text) for p in pagination if p.text.isdigit()])
            except:
                return 1
        return 1

    def get_page_url(self, base_url, page):
        clean_base = base_url.split('?')[0].split('#')[0].rstrip('/')
        return f"{clean_base}/?page={page}#catalog-listing" if page > 1 else f"{clean_base}/"

    def extract_product_details(self, article):
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
                'product_url': self.base_url + product.get('href', '') if product.get('href', '').startswith('/') else product.get('href', '')
            }
            img_tag = product.find('img')
            if img_tag:
                details['image_url'] = img_tag.get('data-src', '') or img_tag.get('src', '')
            price_div = product.find('div', class_='prc')
            if price_div:
                details['displayed_price'] = price_div.text.strip()
            return details
        return None

    def save_data(self, data, filename):
        if not data:
            return None
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{filename}_{timestamp}.csv"
        csv_path = os.path.join(self.data_directory, csv_filename)
        fieldnames = data[0].keys()
        with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Données sauvegardées: {csv_path}")
        return csv_path

    def scrape_category(self, category_info):
        base_url = category_info['href']
        category_name = category_info['text']
        subcategory = category_info['subcategory']
        products = []
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(self.get_page_url(base_url, 1), headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            total_pages = self.get_total_pages(soup)
            print(f"{category_name} ({subcategory}) - Pages totales: {total_pages}")
            for page in range(1, total_pages + 1):
                page_url = self.get_page_url(base_url, page)
                response = requests.get(page_url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for article in soup.find_all('article', class_='prd _fb col c-prd'):
                        product_details = self.extract_product_details(article)
                        if product_details:
                            product_details.update({'subcategory': subcategory, 'category_name': category_name, 'page_number': page})
                            products.append(product_details)
                time.sleep(2)
        return products

    def process_all_categories(self):
        all_products = []
        with open(self.subcategories_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for category in reader:
                products = self.scrape_category(category)
                all_products.extend(products)
                if products:
                    self.save_data(products, f"products_{category['subcategory']}")
        if all_products:
            self.save_data(all_products, 'all_products')
        return all_products

if __name__ == "__main__":
    extractor = JumiaAccInfoExtractor()
    extractor.convert_json_to_csv()
    extractor.process_all_categories()
