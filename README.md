# Projet Automates

Suite d'applications web pour la théorie des automates.

## Prérequis
Installer MySQL (si pas déjà installé)
Ubuntu/Debian :

```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

## Installation

```bash
make install_dep
```

## Configuration BDD

1. Créer la base MySQL :
```sql
CREATE DATABASE automates_db;
```

2. Modifier `automata_webapp/app/__init__.py` :
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:votremotdepasse@localhost/automates_db'
```

## Utilisation :  Entrer la commande : "make help"

```bash
make help              # Voir toutes les commandes
make auto              # App principale (port 5000)  
make system            # Systèmes équations (port 5001)
make auto_util         # Utilitaires (port 5003)
make run-all           # Tous les serveurs
make stop              # Arrêter tous
```

## Modules

- **automata_webapp** : Application principale (port 5000)
- **Systemes_equations** : Systèmes d'équations (port 5001) 
- **Automates_utils** : Utilitaires (port 5003)
