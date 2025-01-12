from bs4 import BeautifulSoup
import json

def clean_brands_to_json():
    try:
        # Lire le fichier marque.txt
        with open('marque.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Parser le HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Trouver tous les liens
        brand_links = soup.find_all('a', class_="fk-cb -me-start -fsh0")
        
        # Créer un dictionnaire pour stocker les informations des marques
        brands_dict = {}
        
        for brand in brand_links:
            brand_name = brand.text.strip()
            brands_dict[brand_name] = {
                'url': brand.get('href'),
                'data_value': brand.get('data-value'),
                'data_label': brand.get('data-eventlabel')
            }
        
        # Sauvegarder en JSON
        with open('marques.json', 'w', encoding='utf-8') as json_file:
            json.dump(brands_dict, json_file, ensure_ascii=False, indent=4)
        
        print("Les marques ont été sauvegardées dans 'marques.json'")
        print(f"Nombre total de marques : {len(brands_dict)}")
        
    except FileNotFoundError:
        print("Le fichier marque.txt n'a pas été trouvé")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    clean_brands_to_json()