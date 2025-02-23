import os
import pandas as pd
from datetime import datetime
import shutil
import glob

class JumiaDataOrganizer:
    def __init__(self):
        # Mise à jour des chemins pour le projet electro
        self.base_directory = "D:/bureau/grand projet/jumia/electro"
        self.data_directory = os.path.join(self.base_directory, 'data/data')
        
        print(f"Base directory: {self.base_directory}")
        print(f"Data directory: {self.data_directory}")
        
        self.ensure_directories()

    def ensure_directories(self):
        """Créer les répertoires nécessaires s'ils n'existent pas"""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            print(f"Créé le répertoire: {self.data_directory}")

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
                    print(f"\nTraitement du fichier: {base_filename}")
                    
                    # Lecture du fichier CSV
                    df = pd.read_csv(source_file)
                    print(f"Lu {len(df)} lignes de données")
                    
                    # Déplacer le fichier dans le nouveau dossier
                    new_filepath = os.path.join(timestamped_folder, base_filename)
                    df.to_csv(new_filepath, index=False)
                    print(f"Fichier déplacé vers: {new_filepath}")
                    
                    # Supprimer le fichier source
                    os.remove(source_file)
                    print(f"Fichier source supprimé: {source_file}")
                    
                    files_processed += 1
                    
                except Exception as e:
                    print(f"Erreur lors du traitement de {base_filename}: {str(e)}")
                    continue

            if files_processed > 0:
                print(f"\nTraitement terminé. {files_processed} fichiers traités avec succès.")
                return True
            else:
                print("Aucun fichier n'a été traité avec succès.")
                return False

        except Exception as e:
            print(f"Erreur lors du traitement des données: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

def main():
    print("Initialisation de l'organisateur de données Jumia Electronics...")
    organizer = JumiaDataOrganizer()

    print("\nTraitement des nouvelles données...")
    if organizer.process_new_data():
        print("\nTraitement des données réussi")
    else:
        print("\nÉchec du traitement des données")

if __name__ == "__main__":
    main()
