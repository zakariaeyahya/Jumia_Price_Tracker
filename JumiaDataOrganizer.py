import os
import pandas as pd
from datetime import datetime
import shutil
import glob

class JumiaDataOrganizer:
    def __init__(self):
        self.base_directory = "D:/bureau/grand projet/jumia/data"
        
        print(f"Base directory: {self.base_directory}")
        self.ensure_base_directory()
        
    def ensure_base_directory(self):
        """S'assurer que le répertoire de base existe"""
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)
            print(f"Créé le répertoire de base: {self.base_directory}")
    
    def get_category_folders(self):
        """Obtenir la liste des dossiers de catégories"""
        category_folders = []
        for item in os.listdir(self.base_directory):
            item_path = os.path.join(self.base_directory, item)
            if os.path.isdir(item_path):
                category_folders.append(item)
        
        print(f"Catégories trouvées: {len(category_folders)}")
        return category_folders
    
    def create_timestamped_folder(self, data_directory):
        """Créer un dossier avec horodatage complet dans le répertoire data d'une catégorie"""
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        timestamped_folder = os.path.join(data_directory, timestamp)
        if not os.path.exists(timestamped_folder):
            os.makedirs(timestamped_folder)
            print(f"Créé le dossier horodaté: {timestamped_folder}")
        return timestamped_folder
    
    def ensure_data_directory(self, category):
        """S'assurer que le répertoire data existe pour une catégorie"""
        data_dir = os.path.join(self.base_directory, category, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"Créé le répertoire data pour {category}: {data_dir}")
        return data_dir
    
    def process_category_data(self, category):
        """Traiter les fichiers CSV dans le répertoire data d'une catégorie"""
        data_dir = self.ensure_data_directory(category)
        
        # Chercher tous les fichiers CSV dans le dossier data
        csv_pattern = os.path.join(data_dir, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            print(f"Aucun fichier CSV trouvé dans {data_dir}")
            return False
        
        # Créer un dossier horodaté pour cette exécution
        timestamped_folder = self.create_timestamped_folder(data_dir)
        files_processed = 0
        
        for source_file in csv_files:
            try:
                # Ne pas traiter les fichiers qui sont déjà dans un dossier horodaté
                if any(d.isdigit() for d in os.path.dirname(source_file).split(os.sep)[-1]):
                    continue
                
                base_filename = os.path.basename(source_file)
                print(f"Traitement de {base_filename} pour {category}...")
                
                # Lire et sauvegarder le fichier dans le nouveau dossier
                df = pd.read_csv(source_file)
                new_filepath = os.path.join(timestamped_folder, base_filename)
                df.to_csv(new_filepath, index=False)
                
                # Supprimer le fichier source après le déplacement
                os.remove(source_file)
                print(f"Fichier traité et déplacé vers: {new_filepath}")
                
                files_processed += 1
            except Exception as e:
                print(f"Erreur lors du traitement de {source_file}: {str(e)}")
        
        return files_processed > 0
    
    def process_all_categories(self):
        """Traiter les données pour toutes les catégories"""
        categories = self.get_category_folders()
        success_count = 0
        
        for category in categories:
            print(f"\nTraitement de la catégorie: {category}")
            if self.process_category_data(category):
                success_count += 1
        
        return success_count

def main():
    print("Initialisation de l'organisateur de données Jumia...")
    organizer = JumiaDataOrganizer()

    print("\nTraitement des données pour toutes les catégories...")
    success_count = organizer.process_all_categories()
    
    if success_count > 0:
        print(f"\nTraitement réussi pour {success_count} catégorie(s)")
    else:
        print("\nAucune donnée n'a été traitée")

if __name__ == "__main__":
    main()