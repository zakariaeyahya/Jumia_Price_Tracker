# Dans le DAG (jumia_scraper_dag.py)
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os
from scripts.jumia_category_scraper import JumiaScraper
from scripts.jumia_product_scraper import JumiaDataExtractor
from scripts.jumia_data_organizer import JumiaDataOrganizer  # Nouveau import

BASE_PATH = "/opt/airflow/data"
HISTORY_FILE = os.path.join(BASE_PATH, "price_history.csv")

def extract_categories():
    scraper = JumiaScraper()
    scraper.scrape_content()

def extract_products():
    extractor = JumiaDataExtractor(BASE_PATH)
    return extractor.process_all_categories()

def update_price_history(**context):
    ti = context['task_instance']
    new_products = ti.xcom_pull(task_ids='extract_products')
    
    new_df = pd.DataFrame(new_products)
    current_date = datetime.now().strftime('%Y-%m-%d')
    price_col = f'price_{current_date}'
    new_df = new_df.rename(columns={'price': price_col})
    
    if os.path.exists(HISTORY_FILE):
        history_df = pd.read_csv(HISTORY_FILE)
        merged_df = pd.merge(
            history_df,
            new_df[['product_id', price_col]],
            on='product_id',
            how='outer'
        )
    else:
        merged_df = new_df
    
    merged_df.to_csv(HISTORY_FILE, index=False)
    return HISTORY_FILE

def organize_data(**context):
    """Nouvelle fonction pour organiser les données"""
    ti = context['task_instance']
    history_file = ti.xcom_pull(task_ids='update_price_history')
    
    organizer = JumiaDataOrganizer(BASE_PATH)
    organizer.process_new_data(history_file)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 26),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'jumia_price_tracker',
    default_args=default_args,
    description='Track Jumia product prices weekly',
    schedule_interval='0 0 * * 0',
    catchup=False
)

task1 = PythonOperator(
    task_id='extract_categories',
    python_callable=extract_categories,
    dag=dag,
)

task2 = PythonOperator(
    task_id='extract_products',
    python_callable=extract_products,
    dag=dag,
)

task3 = PythonOperator(
    task_id='update_price_history',
    python_callable=update_price_history,
    provide_context=True,
    dag=dag,
)

task4 = PythonOperator(
    task_id='organize_data',
    python_callable=organize_data,
    provide_context=True,
    dag=dag,
)

task1 >> task2 >> task3 >> task4