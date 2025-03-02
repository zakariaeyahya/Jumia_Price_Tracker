from bs4 import BeautifulSoup
import requests
import json

# URL de la page
url = "https://www.jumia.ma/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    categories_data = {}
    
    flyout = soup.find('div', class_='flyout-w -fsh0 -fs0')
    
    if flyout:
        print("Conteneur trouvé!")
        
        categories = flyout.find_all('a', class_='itm')
        for category in categories:
            category_name = category.text.strip()
            category_url = category.get('href')  # Récupération de l'URL
            print(f"Traitement de la catégorie : {category_name}")
            
            # Stocker à la fois le nom et l'URL
            categories_data[category_name] = {
                "url": category_url,  # Ajout de l'URL
                "subcategories": {}   # Pour les sous-catégories
            }
            
            sub = category.find_next('div', class_='sub')
            if sub:
                sub_w = sub.find('div', class_='sub-w')
                if sub_w:
                    for cat in sub_w.find_all('div', class_='cat'):
                        title = cat.find('a', class_='tit')
                        if title:
                            section_name = title.text.strip()
                            section_url = title.get('href')  # URL de la section
                            sub_items = cat.find_all('a', class_='s-itm')
                            if sub_items:
                                sub_categories = [
                                    {
                                        "name": item.text.strip(),
                                        "url": item.get('href')  # URL de la sous-catégorie
                                    }
                                    for item in sub_items
                                ]
                                categories_data[category_name]["subcategories"][section_name] = {
                                    "url": section_url,
                                    "items": sub_categories
                                }
                                print(f"  Ajout de {len(sub_categories)} sous-catégories pour {section_name}")
        
        with open('categories_completes.json', 'w', encoding='utf-8') as f:
            json.dump(categories_data, f, ensure_ascii=False, indent=4)
        
        print("\nCatégories et sous-catégories enregistrées dans 'categories_completes.json'")
        
    else:
        print("Conteneur principal non trouvé")
        
except requests.exceptions.RequestException as e:
    print(f"Erreur lors de la requête HTTP : {e}")
except Exception as e:
    print(f"Une erreur est survenue : {e}")
    print("Type d'erreur:", type(e))