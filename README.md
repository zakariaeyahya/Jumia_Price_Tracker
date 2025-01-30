# Jumia Price Tracker 🛒📊

Un projet d'analyse des prix des produits Jumia automatisé avec Apache Airflow.

## 📌 Aperçu du Projet
Ce projet permet de tracker quotidiennement les prix des produits sur Jumia.ma en utilisant :
- **Web Scraping** pour collecter les données
- **Airflow** pour l'orchestration des tâches
- **Pandas** pour le traitement des données
- Un système de stockage organisé avec historique des prix

## ✨ Fonctionnalités Clés
- 🕸 Scraping des catégories et sous-catégories
- 📦 Extraction des détails produits (nom, prix, marque, URL)
- 📅 Historique des prix avec suivi quotidien
- 🗂 Organisation automatique des données par date/catégorie
- ⏲ Exécution planifiée (tous les dimanches à minuit)

## 🗂 Structure du Projet
```
jumia_price_tracker/
├── dags/
│   ├── jumia_scraper_dag.py           # DAG principal Airflow
│   └── scripts/
│       ├── jumia_category_scraper.py  # Scraping des catégories
│       ├── jumia_product_scraper.py   # Extraction des produits
│       └── jumia_data_organizer.py    # Organisation des données
├── data/
│   ├── daily_data/                    # Dossiers par date
│   └── price_history.csv              # Historique consolidé
```

## 🛠 Installation
1. Prérequis :
```bash
Python 3.8+
Apache Airflow 2.0+
pip install -r requirements.txt
```
(requirements.txt)
```
apache-airflow
pandas
requests
beautifulsoup4
```

2. Configuration Airflow :
```bash
export AIRFLOW_HOME=~/airflow
airflow db init
```

## ⚙ Configuration
Modifier ces paramètres dans `jumia_scraper_dag.py` si nécessaire :
```python
BASE_PATH = "/opt/airflow/data"  # Chemin de stockage
SCHEDULE_INTERVAL = '0 0 * * 0'  # Exécution hebdomadaire
```

## ▶ Exécution
1. Démarrer Airflow :
```bash
airflow webserver
airflow scheduler
```
2. Activer le DAG dans l'interface Airflow

## 🔄 Flux de Données
1. `extract_categories` → Scraping de l'arborescence
2. `extract_products` → Extraction des produits
3. `update_price_history` → Mise à jour CSV historique
4. `organize_data` → Archivage quotidien

## 📁 Stockage des Données
Exemple de structure générée :
```
data/
├── daily_data/
│   └── 20240128/
│       ├── jumia_data_20240128.csv
│       └── category_Telephones_20240128.csv
└── price_history.csv
```

## 🔧 Personnalisation
Variables à adapter :
- Catégories cibles : Modifier `start_url` dans `JumiaScraper`
- Fréquence d'exécution : Modifier `schedule_interval` dans le DAG
- Stockage : Modifier `BASE_PATH` selon l'environnement

## 🚨 Dépannage
Problèmes courants :
- Erreurs de scraping → Vérifier les User-Agents
- Problèmes de chemin → Vérifier les permissions
- Données manquantes → Tester avec une seule catégorie

⚠️ **Note** : Respectez le `robots.txt` de Jumia et évitez les requêtes intensives.
