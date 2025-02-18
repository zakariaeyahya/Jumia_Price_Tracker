import os
import pandas as pd
from datetime import datetime
import shutil
import glob

class JumiaDataOrganizer:
    def __init__(self):
        self.base_directory = "/data/jumia"
        self.data_directory = os.path.join(self.base_directory, 'data')
        self.daily_data_path = os.path.join(self.base_directory, 'daily_data')

        # Mettre à jour les chemins
        self.data_directory = os.path.join(self.base_directory, 'data')
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
        for directory in [self.daily_data_path, self.categories_path, self.subcategories_path]:
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

        # Trier par date de modification et prendre le plus récent
        latest_file = max(files, key=os.path.getctime)
        print(f"Fichier le plus récent trouvé: {latest_file}")
        return latest_file

    def create_daily_folder(self):
        """Créer un dossier pour la date du jour"""
        current_date = datetime.now().strftime('%Y%m%d')
        daily_folder = os.path.join(self.daily_data_path, current_date)
        if not os.path.exists(daily_folder):
            os.makedirs(daily_folder)
            print(f"Créé le dossier quotidien: {daily_folder}")
        return daily_folder

    def clean_filename(self, filename):
        """Nettoyer le nom de fichier en retirant les caractères spéciaux"""
        return "".join(c for c in filename if c.isalnum() or c in ['-', '_']).strip()

    def process_new_data(self):
        """Traiter toutes les nouvelles données CSV et les organiser"""
        try:
            # Trouver tous les fichiers CSV dans le dossier data
            csv_pattern = os.path.join(self.data_directory, "*.csv")
            csv_files = glob.glob(csv_pattern)
            
            if not csv_files:
                print(f"Aucun fichier CSV trouvé dans {self.data_directory}")
                return False
                
            # Créer le dossier quotidien
            current_date = datetime.now().strftime('%Y%m%d')
            daily_folder = self.create_daily_folder()
            
            files_processed = 0
            for source_file in csv_files:
                try:
                    # Obtenir le nom de base du fichier
                    base_filename = os.path.basename(source_file)
                    print(f"\nTraitement du fichier: {base_filename}")
                    
                    # Lire le fichier CSV
                    df = pd.read_csv(source_file)
                    print(f"Lu {len(df)} lignes de données")
                    
                    # Créer le nouveau nom de fichier avec la date
                    new_filename = f"{os.path.splitext(base_filename)[0]}_{current_date}.csv"
                    new_filepath = os.path.join(daily_folder, new_filename)
                    
                    # Sauvegarder dans le dossier quotidien
                    df.to_csv(new_filepath, index=False)
                    print(f"Fichier sauvegardé: {new_filepath}")
                    
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

    def archive_old_data(self, days_to_keep=30):
        """Archiver les anciennes données"""
        try:
            current_date = datetime.now()
            archive_dir = os.path.join(self.daily_data_path, 'archives')

            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)

            for folder_name in os.listdir(self.daily_data_path):
                folder_path = os.path.join(self.daily_data_path, folder_name)
                if os.path.isdir(folder_path) and folder_name != 'archives':
                    try:
                        folder_date = datetime.strptime(folder_name, '%Y%m%d')
                        days_old = (current_date - folder_date).days

                        if days_old > days_to_keep:
                            # Créer un fichier zip avant de supprimer
                            archive_name = f"{folder_name}_archive.zip"
                            archive_path = os.path.join(archive_dir, archive_name)

                            shutil.make_archive(
                                os.path.splitext(archive_path)[0],
                                'zip',
                                folder_path
                            )

                            # Supprimer le dossier original
                            shutil.rmtree(folder_path)
                            print(f"Dossier archivé et supprimé: {folder_path}")

                    except ValueError:
                        print(f"Format de dossier invalide ignoré: {folder_name}")
                        continue

            return True

        except Exception as e:
            print(f"Erreur lors de l'archivage: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

def main():
    print("Initialisation de l'organisateur de données Jumia...")
    organizer = JumiaDataOrganizer()

    print("\nTraitement des nouvelles données...")
    if organizer.process_new_data():
        print("\nTraitement des données réussi")

        print("\nArchivage des anciennes données...")
        if organizer.archive_old_data():
            print("Archivage des anciennes données réussi")
        else:
            print("Attention: Échec de l'archivage des anciennes données")
    else:
        print("\nÉchec du traitement des données")

if __name__ == "__main__":
    main()
