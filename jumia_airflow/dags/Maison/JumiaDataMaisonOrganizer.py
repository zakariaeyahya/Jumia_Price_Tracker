import os
import pandas as pd
from datetime import datetime
import shutil
import glob

class JumiaDataOrganizer:
    def __init__(self):
        self.base_directory = "D:/bureau/grand projet/jumia/Maison"
        self.data_directory = os.path.join(self.base_directory, 'data/data')  # Changé pour correspondre au chemin souhaité
        self.daily_data_path = os.path.join(self.base_directory, 'daily_data')
        self.categories_path = os.path.join(self.base_directory, 'categories')
        self.subcategories_path = os.path.join(self.base_directory, 'subcategories')

        print(f"Base directory: {self.base_directory}")
        print(f"Data directory: {self.data_directory}")
        print(f"Daily data path: {self.daily_data_path}")
        print(f"Categories path: {self.categories_path}")
        print(f"Subcategories path: {self.subcategories_path}")

        self.ensure_directories()

    def ensure_directories(self):
        """Créer les répertoires nécessaires s'ils n'existent pas"""
        for directory in [self.data_directory, self.categories_path, self.subcategories_path]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Créé le répertoire: {directory}")

    def get_latest_all_products_file(self):
        """Trouver le fichier all_products le plus récent"""
        pattern = os.path.join(self.data_directory, "all_products_*.csv")
        files = glob.glob(pattern)
        if not files:
            print(f"Aucun fichier all_products trouvé dans {self.data_directory}")
            return None
        latest_file = max(files, key=os.path.getctime)
        print(f"Fichier le plus récent trouvé: {latest_file}")
        return latest_file

    def create_timestamped_folder(self):
        """Créer un dossier avec horodatage complet"""
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        timestamped_folder = os.path.join(self.data_directory, timestamp)
        if not os.path.exists(timestamped_folder):
            os.makedirs(timestamped_folder)
            print(f"Créé le dossier horodaté: {timestamped_folder}")
        return timestamped_folder

    def process_new_data(self):
        """Traiter toutes les nouvelles données CSV et les organiser"""
        try:
            csv_pattern = os.path.join(self.data_directory, "*.csv")
            csv_files = glob.glob(csv_pattern)
            if not csv_files:
                print(f"Aucun fichier CSV trouvé dans {self.data_directory}")
                return False

            timestamped_folder = self.create_timestamped_folder()
            files_processed = 0
            
            for source_file in csv_files:
                try:
                    base_filename = os.path.basename(source_file)
                    df = pd.read_csv(source_file)
                    new_filepath = os.path.join(timestamped_folder, base_filename)
                    df.to_csv(new_filepath, index=False)
                    print(f"Fichier déplacé vers: {new_filepath}")
                    files_processed += 1
                    
                    # Supprimer le fichier source après le déplacement
                    os.remove(source_file)
                    print(f"Fichier source supprimé: {source_file}")
                    
                except Exception as e:
                    print(f"Erreur lors du traitement de {base_filename}: {str(e)}")
                    continue

            return files_processed > 0
        except Exception as e:
            print(f"Erreur lors du traitement des données: {str(e)}")
            return False

def main():
    print("Initialisation de l'organisateur de données Jumia...")
    organizer = JumiaDataOrganizer()

    print("\nTraitement des nouvelles données...")
    if organizer.process_new_data():
        print("\nTraitement des données réussi")
    else:
        print("\nÉchec du traitement des données")

if __name__ == "__main__":
    main()
