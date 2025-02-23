import requests 
from bs4 import BeautifulSoup
import json
import os
import time

class JumiaAccInfoScraper:
    def __init__(self):
        self.base_directory = "D:/bureau/grand projet/jumia/acc_info/data"  # Chemin local
        self.data_directory = self.base_directory
        
        self.base_url = "https://www.jumia.ma"
        self.start_url = "https://www.jumia.ma/ordinateurs-accessoires-informatique/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Créé le répertoire: {path}")
            
    def save_json(self, data, filename):
        full_path = os.path.join(self.data_directory, filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Fichier sauvegardé: {full_path}")
            
    def get_page_content(self, url):
        try:
            print(f"Récupération de la page : {url}")
            response = requests.get(url, headers=self.headers)
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Erreur lors de la récupération de {url}: {e}")
            return None
            
    def extract_elements(self, soup):
        elements = soup.find_all(class_="-db -pvs -phxl -hov-bg-gy05")
        elements_data = []
        for element in elements:
            href = element.get('href', '')
            elements_data.append({
                "text": element.text.strip(),
                "html": str(element),
                "href": href
            })
        return elements_data
            
    def scrape_content(self):
        try:
            print("Début du scraping...")
            print(f"Dossier de base: {self.base_directory}")
            print(f"Dossier de données: {self.data_directory}")
            
            for subdir in ['elements', 'categories', 'subcategories']:
                self.create_directory(os.path.join(self.data_directory, subdir))
            
            main_soup = self.get_page_content(self.start_url)
            if not main_soup:
                return False
                
            main_elements = self.extract_elements(main_soup)
            self.save_json(main_elements, "elements/elements.json")
            
            all_categories = []
            
            for element in main_elements:
                href = element.get('href', '')
                if href:
                    full_url = self.base_url + href if not href.startswith('http') else href
                    category_data = {
                        "category": element["text"],
                        "url": full_url,
                        "sub_elements": []
                    }
                    
                    print(f"\nScraping de la catégorie : {element['text']}")
                    sub_soup = self.get_page_content(full_url)
                    if sub_soup:
                        sub_elements = self.extract_elements(sub_soup)
                        category_data["sub_elements"] = sub_elements
                        
                        safe_filename = "".join(x for x in element["text"] if x.isalnum() or x in [' ', '-', '_']).rstrip()
                        safe_filename = safe_filename.replace(' ', '_')
                        self.save_json(sub_elements, f"subcategories/{safe_filename}.json")
                        print(f"Sous-éléments sauvegardés pour {element['text']} ({len(sub_elements)} éléments)")
                        
                    all_categories.append(category_data)
                    time.sleep(1)
            
            self.save_json(all_categories, "categories/all_categories.json")
            
            print("\nScraping terminé avec succès!")
            return True
            
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            import traceback
            print(traceback.format_exc())
            return False

if __name__ == "__main__":
    scraper = JumiaAccInfoScraper()
    scraper.scrape_content()
