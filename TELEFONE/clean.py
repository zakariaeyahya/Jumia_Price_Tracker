from bs4 import BeautifulSoup
import json

def clean_and_save_to_json():
    try:
        # Lire le fichier jumia_elements.txt
        with open('jumia_elements.txt', 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Parser le HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Trouver tous les liens
        links = soup.find_all('a', class_="-db -pvs -phxl -hov-bg-gy05")
        
        # Créer un dictionnaire pour le JSON
        categories = {}
        for link in links:
            category_name = link.text.strip()
            categories[category_name] = {
                'url': link.get('href'),
                'id': link.get('data-eventlabel')
            }
        
        # Sauvegarder en JSON
        with open('categories.json', 'w', encoding='utf-8') as json_file:
            json.dump(categories, json_file, ensure_ascii=False, indent=4)
            
        print("Données sauvegardées dans categories.json")
        
    except FileNotFoundError:
        print("Le fichier jumia_elements.txt n'a pas été trouvé")
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")

# Exécuter le script
if __name__ == "__main__":
    clean_and_save_to_json()