from datetime import datetime, timedelta
import os
import sys

import sys
import sys
sys.path.append('/opt/airflow/jumia')

from JumiaAllScraper import JumiaScraper
from UnifiedJumiaScraper import UnifiedJumiaScraper
from JumiaDataOrganizer import JumiaDataOrganizer




# Import Airflow modules
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define functions that will be called by Airflow tasks
def run_initial_scraper(**kwargs):
    """Run the initial scraper to extract categories and subcategories."""
    print("Starting initial category and subcategory scraping...")
    
    # Load categories from JSON file
    import json
    with open("/opt/airflow/jumia/categories_completes.json", "r", encoding="utf-8") as f:

        categories = json.load(f)
    
    # Process each category
    results = {}
    for category_name, category_info in categories.items():
        print(f"Processing category: {category_name}")
        scraper = JumiaScraper(category_name, category_info["url"])
        success = scraper.scrape_content()
        results[category_name] = "Success" if success else "Failed"
    
    # Return results for logging
    return results

def run_unified_scraper(**kwargs):
    """Run the unified scraper to extract product details."""
    print("Starting unified product scraping...")
    
    # Initialize and run the scraper
    scraper = UnifiedJumiaScraper()
    scraper.process_all_categories()
    
    print("Unified product scraping completed.")
    return {"status": "completed"}

def organize_scraped_data(**kwargs):
    """Run the data organizer to arrange and archive scraped data."""
    print("Starting data organization process...")
    
    # Initialize and run the organizer
    organizer = JumiaDataOrganizer()
    success_count = organizer.process_all_categories()
    
    print(f"Data organization completed. Processed {success_count} categories.")
    return {"categories_processed": success_count}

# Create the DAG
dag = DAG(
    'jumia_scraper_workflow',
    default_args=default_args,
    description='A workflow to scrape Jumia categories, products, and organize data',
    schedule_interval=timedelta(days=1),  # Run daily
    start_date=days_ago(1),
    tags=['jumia', 'scraping', 'ecommerce'],
)

# Define the tasks in the DAG
task_initial_scrape = PythonOperator(
    task_id='initial_category_scrape',
    python_callable=run_initial_scraper,
    provide_context=True,
    dag=dag,
)

task_unified_scrape = PythonOperator(
    task_id='unified_product_scrape',
    python_callable=run_unified_scraper,
    provide_context=True,
    dag=dag,
)

task_organize_data = PythonOperator(
    task_id='organize_data',
    python_callable=organize_scraped_data,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
task_initial_scrape >> task_unified_scrape >> task_organize_data
