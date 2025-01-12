import requests 
from bs4 import BeautifulSoup

def scrape_jumia():
    url = "https://www.jumia.ma/telephone-tablette/n"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Chercher les éléments avec la classe spécifique
        elements = soup.find_all(class_="-db -pvs -phxl -hov-bg-gy05")
        
        # Sauvegarder dans un fichier
        with open('jumia_elements.txt', 'w', encoding='utf-8') as file:
            for element in elements:
                file.write(str(element))
                file.write('\n\n')  # Ajouter des sauts de ligne entre les éléments
        
        print(f"Nombre d'éléments trouvés : {len(elements)}")
        
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    scrape_jumia()