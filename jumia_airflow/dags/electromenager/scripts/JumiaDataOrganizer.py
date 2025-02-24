import os
import glob
from datetime import datetime
import shutil

class JumiaDataOrganizer:
    def __init__(self):
        self.base_directory = "D:/bureau/grand projet/jumia/electromenager"
        self.data_directory = os.path.join(self.base_directory, 'data')
        print(f"Base directory: {self.base_directory}")
        print(f"Data directory: {self.data_directory}")
        self.ensure_directories()

    def ensure_directories(self):
        """Créer les répertoires nécessaires s'ils n'existent pas"""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            print(f"Créé le répertoire: {self.data_directory}")

    def create_timestamped_folder(self):
        """Créer un dossier avec horodatage complet (YYYY_MM_DD_HH_MM_SS)"""
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        timestamped_folder = os.path.join(self.data_directory, timestamp)
        
        if not os.path.exists(timestamped_folder):
            os.makedirs(timestamped_folder)
            print(f"Créé le dossier horodaté: {timestamped_folder}")
        else:
            print(f"Le dossier existe déjà: {timestamped_folder}")
        
        return timestamped_folder
    
    def move_latest_file(self, destination_folder):
        """Déplacer le dernier fichier CSV généré vers le dossier horodaté"""
        pattern = os.path.join(self.data_directory, "products_electromenager_*.csv")
        files = glob.glob(pattern)
        if not files:
            print("Aucun fichier CSV trouvé à déplacer.")
            return
        
        latest_file = max(files, key=os.path.getctime)
        print(f"Dernier fichier trouvé: {latest_file}")
        
        destination_path = os.path.join(destination_folder, os.path.basename(latest_file))
        shutil.move(latest_file, destination_path)
        print(f"Fichier déplacé vers: {destination_path}")


def main():
    print("Initialisation de l'organisateur de données Jumia Electromenager...")
    organizer = JumiaDataOrganizer()
    
    print("\nCréation du dossier horodaté...")
    new_folder = organizer.create_timestamped_folder()
    
    print("\nDéplacement du dernier fichier généré...")
    organizer.move_latest_file(new_folder)

if __name__ == "__main__":
    main()