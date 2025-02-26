# Jumia Price Tracker

## Description

Jumia Price Tracker est un système automatisé de surveillance des prix sur Jumia.ma. Il collecte quotidiennement les données des produits, les organise et maintient un historique des prix pour analyse.

## Fonctionnalités

- 🔍 Extraction automatique des catégories et sous-catégories
- 📊 Collecte des données produits (prix, caractéristiques, etc.)
- 📅 Organisation quotidienne des données
- 📦 Archivage automatique des données anciennes
- 🔄 Pipeline Airflow pour l'automatisation complète

## Prérequis

- Python 3.8+
- Apache Airflow 2.0+
- Pandas
- BeautifulSoup4
- Requests

## Installation

### Cloner le repository

```bash
git clone https://github.com/zakariaeyahya/Jumia_Price_Tracker.git
cd Jumia_Price_Tracker
```

### Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

### Configurer Airflow

```bash
export AIRFLOW_HOME=~/airflow
airflow db init
```

## Structure du Projet

```
Jumia_Price_Tracker/
├── airflow/
│   └── dags/
│       └── jumia_price_tracker_dag.py
├── scripts/
│   ├── jumia_category_scraper.py
│   ├── jumia_product_scraper.py
│   └── jumia_data_organizer.py
├── data/
│   └── README.md
├── daily_data/
│   ├── YYYYMMDD/
│   └── archives/
├── requirements.txt
└── README.md
```

## Configuration

### Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```
JUMIA_BASE_URL=https://www.jumia.ma
AIRFLOW_HOME=/chemin/vers/airflow
```

### Configuration Airflow

Le DAG est configuré pour s'exécuter quotidiennement à midi :

```python
schedule_interval='0 12 * * *'
```

## Utilisation

### Via Airflow UI

#### Démarrer le webserver Airflow

```bash
airflow webserver --port 8080
```

#### Démarrer le scheduler

```bash
airflow scheduler
```

#### Accéder à l'interface Airflow

[http://localhost:8080](http://localhost:8080)

#### Activer le DAG 'jumia_price_tracker'

### Exécution Manuelle

Les scripts peuvent être exécutés individuellement :

```bash
python scripts/jumia_category_scraper.py
python scripts/jumia_product_scraper.py
python scripts/jumia_data_organizer.py
```

## Données Collectées

### Format des Données

Les données sont sauvegardées en CSV avec les champs suivants :

- `name` : Nom du produit
- `price` : Prix actuel
- `brand` : Marque
- `category` : Catégorie
- `displayed_price` : Prix affiché
- `product_url` : URL du produit
- etc.

### Organisation

- Données quotidiennes : `/daily_data/YYYYMMDD/`
- Archives : `/daily_data/archives/`
- Données par catégorie : `/daily_data/YYYYMMDD/category_*`

## Maintenance

### Tâches Régulières

- Vérifier l'espace disque disponible
- Monitorer les logs Airflow
- Vérifier les archives
- Nettoyer les données temporaires

## Dépannage

- Vérifier les logs dans `/airflow/logs/`
- Consulter le statut des tâches dans l'UI Airflow
- Vérifier les fichiers CSV générés

## Contribution

- Fork le projet
- Créer une branche (`git checkout -b feature/ma-feature`)
- Commit les changements (`git commit -m 'Ajout de ma feature'`)
- Push vers la branche (`git push origin feature/ma-feature`)
- Créer une Pull Request

## Sécurité

- Ne pas commiter de données sensibles
- Utiliser des variables d'environnement
- Respecter les règles de scraping de Jumia
- Implémenter des délais entre les requêtes

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Contact

Pour toute question ou suggestion :

- Email : zakariae.yh@gmail.com
- Issues : [https://github.com/zakariaeyahya/Jumia_Price_Tracker/issues](https://github.com/zakariaeyahya/Jumia_Price_Tracker/issues)

## Remerciements

- Équipe Airflow pour leur excellent framework
- Contributeurs du projet
- Communauté Python pour les outils et bibliothèques
