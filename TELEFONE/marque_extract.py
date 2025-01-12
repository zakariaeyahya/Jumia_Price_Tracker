import requests 
from bs4 import BeautifulSoup

def scrape_jumia_brands():
    url = "https://www.jumia.ma/telephone-tablette/n"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    
    try:
        # Faire la requête
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver tous les éléments avec la classe spécifique
        brand_elements = soup.find_all(class_="fk-cb -me-start -fsh0")
        
        # Sauvegarder dans un fichier
        with open('marque.txt', 'w', encoding='utf-8') as file:
            for element in brand_elements:
                file.write(str(element))
                file.write('\n---\n')  # Séparateur entre les éléments
        
        print(f"Nombre de marques trouvées : {len(brand_elements)}")
        print("Les marques ont été sauvegardées dans 'marque.txt'")
        
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    scrape_jumia_brands()