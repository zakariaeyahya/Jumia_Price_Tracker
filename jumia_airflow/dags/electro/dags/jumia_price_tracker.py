# dags/jumia_price_tracker.py
from airflow import DAG
from airflow.operators.python import PythonOperator 
from datetime import datetime, timedelta
import os
import sys

# Ajouter le chemin des scripts au PYTHONPATH
scripts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
sys.path.append(scripts_path)

from JumiaElectronicsScraper import JumiaElectronicsScraper
from JumiaElectronicsExtractor import JumiaElectronicsExtractor
from JumiaDataOrganizer import JumiaDataOrganizer

# Définir le chemin de base en utilisant des forward slashes pour Docker
BASE_PATH = "/data/jumia"

def extract_categories(**context):
   """Extraire les catégories de Jumia"""
   print("Début de l'extraction des catégories...")
   scraper = JumiaElectronicsScraper()
   success = scraper.scrape_content()
   
   if not success:
       raise Exception("Échec de l'extraction des catégories")
   
   return "Catégories extraites avec succès"

def extract_products(**context):
   """Extraire les produits de toutes les catégories"""
   print("Début de l'extraction des produits...")
   extractor = JumiaElectronicsExtractor()
   
   csv_path = extractor.convert_json_to_csv()
   if not csv_path:
       raise Exception("Échec de la conversion JSON vers CSV")
       
   products = extractor.process_all_categories()
   if not products:
       raise Exception("Aucun produit extrait")
   
   return "Produits extraits avec succès"

def organize_data(**context):
   """Organiser les données collectées"""
   print("Début de l'organisation des données...")
   organizer = JumiaDataOrganizer()
   
   if not organizer.process_new_data():
       raise Exception("Échec de l'organisation des données")
   
   if not organizer.archive_old_data(days_to_keep=30):
       print("Attention: Échec de l'archivage des anciennes données")
   
   return "Données organisées avec succès"

# Configuration du DAG
default_args = {
   'owner': 'airflow',
   'depends_on_past': False,
   'email_on_failure': True,
   'email_on_retry': False,
   'retries': 1,
   'retry_delay': timedelta(minutes=5),
}

with DAG(
   'jumia_electronics_tracker',
   default_args=default_args,
   description='Suivi quotidien des prix Jumia Électronique',
   schedule_interval='0 12 * * *',  # Tous les jours à midi
   start_date=datetime(2025, 2, 16),
   catchup=False,
   tags=['jumia', 'electronics', 'scraping', 'prices'],
) as dag:
   
   # Tâche 1: Extraction des catégories
   task1 = PythonOperator(
       task_id='extract_categories',
       python_callable=extract_categories,
       doc_md="""
       ### Extraction des catégories
       Cette tâche extrait toutes les catégories et sous-catégories de la section électronique de Jumia.
       Les données sont sauvegardées au format JSON.
       """,
   )
   
   # Tâche 2: Extraction des produits
   task2 = PythonOperator(
       task_id='extract_products',
       python_callable=extract_products,
       doc_md="""
       ### Extraction des produits
       Cette tâche:
       1. Convertit les données JSON en CSV
       2. Extrait tous les produits de chaque catégorie
       3. Sauvegarde les données au format CSV
       """,
   )
   
   # Tâche 3: Organisation des données
   task3 = PythonOperator(
       task_id='organize_data',
       python_callable=organize_data,
       doc_md="""
       ### Organisation des données
       Cette tâche:
       1. Organise les données par date et catégorie
       2. Archive les anciennes données
       3. Maintient une structure de dossiers propre
       """,
   )
   
   # Définir l'ordre des tâches
   task1 >> task2 >> task3