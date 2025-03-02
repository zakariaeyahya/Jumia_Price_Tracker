import json
import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class UnifiedJumiaScraper:
    def __init__(self):
        self.base_directory = "D:/bureau/grand projet/jumia/data"
        self.base_url = "https://www.jumia.ma"
        
        # Catégories spéciales qui n'ont pas de sous-catégories
        self.special_categories = {
            "Bricolage": "https://www.jumia.ma/mlp-bricolage-et-jardinage/",
            "Électroménager": "https://www.jumia.ma/mlp-electromenager/"
        }
        
        print(f"Base directory: {self.base_directory}")
        self.ensure_directories()

    def ensure_directories(self):
        """S'assure que tous les dossiers nécessaires existent."""
        # Créer le dossier principal s'il n'existe pas
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)
            print(f"Dossier principal créé: {self.base_directory}")
            
        # Parcourir toutes les catégories et créer un dossier data pour chacune
        for category_dir in os.listdir(self.base_directory):
            category_path = os.path.join(self.base_directory, category_dir)
            if os.path.isdir(category_path):
                data_dir = os.path.join(category_path, 'data')
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                    print(f"Dossier data créé pour la catégorie {category_dir}")
        
        # Créer les dossiers pour les catégories spéciales si nécessaire
        for category in self.special_categories.keys():
            category_path = os.path.join(self.base_directory, category)
            data_dir = os.path.join(category_path, 'data')
            if not os.path.exists(category_path):
                os.makedirs(category_path)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Dossier data créé pour la catégorie spéciale {category}")

    def extract_subcategories_for_category(self, category_dir):
        """Extrait les sous-catégories pour une catégorie spécifique."""
        subcategories = []
        subcategories_dir = os.path.join(self.base_directory, category_dir, 'subcategories')
        
        if not os.path.exists(subcategories_dir) or not os.path.isdir(subcategories_dir):
            print(f"Dossier subcategories non trouvé pour {category_dir}")
            return subcategories
            
        # Parcourir tous les fichiers JSON dans le dossier subcategories
        for file_name in os.listdir(subcategories_dir):
            if file_name.endswith('.json'):
                file_path = os.path.join(subcategories_dir, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Traiter les différentes structures possibles de JSON
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    subcategory = {
                                        'text': item.get('text', item.get('category', '')),
                                        'href': item.get('href', item.get('url', '')),
                                        'subcategory': item.get('subcategory', os.path.splitext(file_name)[0])
                                    }
                                    
                                    # Assurer que l'URL commence par http
                                    if subcategory['href'] and not subcategory['href'].startswith('http'):
                                        subcategory['href'] = self.base_url + ('' if subcategory['href'].startswith('/') else '/') + subcategory['href']
                                        
                                    subcategories.append(subcategory)
                        elif isinstance(data, dict):
                            subcategory = {
                                'text': data.get('text', data.get('category', '')),
                                'href': data.get('href', data.get('url', '')),
                                'subcategory': data.get('subcategory', os.path.splitext(file_name)[0])
                            }
                            
                            # Assurer que l'URL commence par http
                            if subcategory['href'] and not subcategory['href'].startswith('http'):
                                subcategory['href'] = self.base_url + ('' if subcategory['href'].startswith('/') else '/') + subcategory['href']
                                
                            subcategories.append(subcategory)
                except Exception as e:
                    print(f"Erreur lors de la lecture de {file_path}: {e}")
                    
        print(f"Extrait {len(subcategories)} sous-catégories pour {category_dir}")
        return subcategories

    def save_subcategories_csv(self, category_dir, subcategories):
        """Sauvegarde les sous-catégories dans un fichier CSV pour une catégorie."""
        if not subcategories:
            return None
            
        csv_path = os.path.join(self.base_directory, category_dir, 'data', 'subcategories.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'href', 'subcategory'])
            writer.writeheader()
            writer.writerows(subcategories)
            
        print(f"CSV des sous-catégories créé: {csv_path}")
        return csv_path

    def get_total_pages(self, soup):
        """Récupère le nombre total de pages d'une catégorie."""
        pagination = soup.find_all('a', {'class': 'pg'})
        if pagination:
            try:
                return max([int(p.text) for p in pagination if p.text.isdigit()])
            except:
                return 1
        return 1

    def get_page_url(self, base_url, page):
        """Construit l'URL d'une page spécifique."""
        clean_base = base_url.split('?')[0].split('#')[0].rstrip('/')
        return f"{clean_base}/?page={page}#catalog-listing" if page > 1 else f"{clean_base}/"

    def extract_product_details(self, article):
        """Extrait les détails d'un produit sur Jumia."""
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

    def save_data(self, category_dir, subcategory, data, filename):
        """Sauvegarde les données extraites dans un fichier CSV."""
        if not data:
            return None
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{filename}_{timestamp}.csv"
        csv_path = os.path.join(self.base_directory, category_dir, 'data', csv_filename)
        
        fieldnames = data[0].keys()
        with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Données sauvegardées: {csv_path}")
        return csv_path

    def scrape_subcategory(self, category_dir, subcategory_info):
        """Scrape une sous-catégorie et extrait les produits."""
        try:
            base_url = subcategory_info['href']
            subcategory_name = subcategory_info['subcategory']
            category_name = subcategory_info['text']
            
            print(f"Scraping de {category_dir}/{subcategory_name} - URL: {base_url}")
            
            products = []
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            response = requests.get(self.get_page_url(base_url, 1), headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                total_pages = self.get_total_pages(soup)
                print(f"{category_name} ({subcategory_name}) - Pages totales: {total_pages}")

                for page in range(1, total_pages + 1):
                    page_url = self.get_page_url(base_url, page)
                    print(f"Traitement de la page {page}/{total_pages}: {page_url}")
                    
                    try:
                        if page > 1:  # La première page est déjà chargée
                            response = requests.get(page_url, headers=headers)
                            soup = BeautifulSoup(response.text, 'html.parser')
                        
                        articles = soup.find_all('article', class_='prd _fb col c-prd')
                        
                        print(f"Trouvé {len(articles)} produits sur la page {page}")
                        
                        for article in articles:
                            product_details = self.extract_product_details(article)
                            if product_details:
                                product_details.update({
                                    'subcategory': subcategory_name,
                                    'category_name': category_name,
                                    'page_number': page,
                                    'page_url': page_url
                                })
                                products.append(product_details)
                    except Exception as e:
                        print(f"Erreur lors du traitement de la page {page}: {e}")
                        
                    # Attendre entre les requêtes pour éviter d'être bloqué
                    time.sleep(2)
            else:
                print(f"Erreur HTTP {response.status_code} pour {base_url}")
                
            return products
        except Exception as e:
            print(f"Erreur lors du scraping de {subcategory_info}: {e}")
            return []

    def scrape_special_category(self, category_name, category_url):
        """Scrape une catégorie spéciale sans sous-catégories."""
        print(f"\nScraping de la catégorie spéciale: {category_name} - URL: {category_url}")
        
        products = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(category_url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            total_pages = self.get_total_pages(soup)
            print(f"{category_name} - Pages totales: {total_pages}")

            for page in range(1, total_pages + 1):
                page_url = f"{category_url}?page={page}#catalog-listing" if page > 1 else category_url
                print(f"Traitement de la page {page}/{total_pages}: {page_url}")
                
                try:
                    if page > 1:  # La première page est déjà chargée
                        response = requests.get(page_url, headers=headers)
                        soup = BeautifulSoup(response.text, 'html.parser')
                    
                    articles = soup.find_all('article', class_='prd _fb col c-prd')
                    
                    print(f"Trouvé {len(articles)} produits sur la page {page}")
                    
                    for article in articles:
                        product_details = self.extract_product_details(article)
                        if product_details:
                            product_details.update({
                                'subcategory': 'main',  # Pas de sous-catégorie
                                'category_name': category_name,
                                'page_number': page,
                                'page_url': page_url
                            })
                            products.append(product_details)
                except Exception as e:
                    print(f"Erreur lors du traitement de la page {page}: {e}")
                    
                # Attendre entre les requêtes pour éviter d'être bloqué
                time.sleep(2)
        else:
            print(f"Erreur HTTP {response.status_code} pour {category_url}")
            
        return products

    def process_all_categories(self):
        """Parcourt toutes les catégories principales et traite leurs sous-catégories."""
        # Traiter d'abord les catégories spéciales sans sous-catégories
        for category_name, category_url in self.special_categories.items():
            print(f"\nTraitement de la catégorie spéciale: {category_name}")
            products = self.scrape_special_category(category_name, category_url)
            if products:
                self.save_data(category_name, '', products, f"products_{category_name.replace(' ', '_')}")
            else:
                print(f"Aucun produit trouvé pour la catégorie spéciale {category_name}")
        
        # Ensuite traiter les catégories normales avec sous-catégories
        for category_dir in os.listdir(self.base_directory):
            category_path = os.path.join(self.base_directory, category_dir)
            
            # Ignorer les dossiers des catégories spéciales déjà traitées
            if not os.path.isdir(category_path) or category_dir in self.special_categories:
                continue
                
            print(f"\nTraitement de la catégorie: {category_dir}")
            
            # Extraire les sous-catégories pour cette catégorie
            subcategories = self.extract_subcategories_for_category(category_dir)
            
            if subcategories:
                # Sauvegarder les sous-catégories dans un fichier CSV
                self.save_subcategories_csv(category_dir, subcategories)
                
                # Traiter chaque sous-catégorie
                all_products = []
                for subcategory in subcategories:
                    if not subcategory['href']:
                        print(f"URL manquante pour {subcategory['subcategory']}, passage à la suivante")
                        continue
                        
                    print(f"\nScraping de la sous-catégorie: {subcategory['subcategory']}")
                    products = self.scrape_subcategory(category_dir, subcategory)
                    
                    if products:
                        all_products.extend(products)
                        # Sauvegarder les produits de cette sous-catégorie
                        self.save_data(
                            category_dir, 
                            subcategory['subcategory'], 
                            products, 
                            f"products_{subcategory['subcategory']}"
                        )
                
                # Sauvegarder tous les produits de cette catégorie
                if all_products:
                    self.save_data(category_dir, '', all_products, f"all_products_{category_dir.replace(' ', '_')}")
            else:
                print(f"Aucune sous-catégorie trouvée pour {category_dir}")

if __name__ == "__main__":
    scraper = UnifiedJumiaScraper()
    scraper.process_all_categories()