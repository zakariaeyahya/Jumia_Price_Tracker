# dags/scripts/jumia_data_organizer.py
import os
import pandas as pd
from datetime import datetime
import shutil

class JumiaDataOrganizer:
    def __init__(self, base_path):
        self.base_path = base_path
        self.daily_data_path = os.path.join(base_path, "daily_data")
        self.ensure_directories()

    def ensure_directories(self):
        if not os.path.exists(self.daily_data_path):
            os.makedirs(self.daily_data_path)

    def create_daily_folder(self):
        current_date = datetime.now().strftime('%Y%m%d')
        daily_folder = os.path.join(self.daily_data_path, current_date)
        if not os.path.exists(daily_folder):
            os.makedirs(daily_folder)
        return daily_folder

    def process_new_data(self, source_file):
        try:
            # Lire les données source
            df = pd.read_csv(source_file)
            current_date = datetime.now().strftime('%Y%m%d')
            
            # Créer le dossier quotidien
            daily_folder = self.create_daily_folder()
            
            # Sauvegarder le fichier complet
            daily_file = os.path.join(daily_folder, f"jumia_data_{current_date}.csv")
            df.to_csv(daily_file, index=False)
            
            # Créer des fichiers par catégorie
            for category in df['category'].unique():
                category_data = df[df['category'] == category]
                category_file = os.path.join(
                    daily_folder, 
                    f"category_{category.replace('/', '_')}_{current_date}.csv"
                )
                category_data.to_csv(category_file, index=False)
            
            print(f"Données traitées avec succès pour la date {current_date}")
            return True
            
        except Exception as e:
            print(f"Erreur lors du traitement des données: {str(e)}")
            return False