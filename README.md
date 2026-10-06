# StockTN Desktop

## Description

StockTN Desktop est une application de bureau destinée à la gestion professionnelle de stock et de commerce en Tunisie. Elle permet de piloter le catalogue produits, le stock, la caisse, les achats, les clients, les fournisseurs, les commandes et les rapports, avec des montants exprimés en dinars tunisiens (TND). L’interface graphique est construite avec CustomTkinter. Les données sont persistées localement sous forme de fichiers JSON, sans serveur distant ni base de données relationnelle.

## Fonctionnalités

L’application propose une authentification par nom d’utilisateur et mot de passe, avec trois rôles (administrateur, vendeur, client) et des menus adaptés à chaque profil. L’administrateur dispose d’un tableau de bord (indicateurs, alertes stock, graphique des ventes sur 7 jours), de la gestion des produits (code, code-barres, catégorie, marque, prix d’achat et de vente, stock minimum, image), des catégories, des mouvements de stock (entrées et sorties avec motif), de la caisse et des ventes (panier, modes de paiement Espèces, Carte, Chèque ou Virement), des achats fournisseurs, du fichier clients et fournisseurs, des commandes (statuts En attente, Confirmée, En préparation, Prête, Terminée, Annulée), de la gestion des utilisateurs et des rapports exportables en CSV, Excel ou PDF. Les vendeurs accèdent au tableau de bord, aux produits, à la caisse, aux clients et aux commandes. Les clients consultent le catalogue, leurs commandes et leur profil. Une sauvegarde et une restauration des fichiers JSON (archives ZIP) sont disponibles pour l’administrateur.

## Technologies utilisées

Le projet est développé en Python. L’interface repose sur CustomTkinter, avec des graphiques Matplotlib et le traitement d’images via Pillow. L’export des rapports utilise openpyxl pour Excel et reportlab pour le PDF. La bibliothèque standard Python fournit le stockage JSON, le hachage des mots de passe (hashlib, secrets), la compression ZIP des sauvegardes et l’export CSV. Aucune base de données SQL ni framework web n’est utilisé.

## Architecture du projet

Le point d’entrée est `main.py`, qui initialise la fenêtre `StockTNApp`, le contexte applicatif `AppContext` et bascule entre l’écran de connexion et la fenêtre principale. La couche `ui/` contient les vues (login, dashboard, produits, catégories, stock, ventes, achats, clients, fournisseurs, commandes, utilisateurs, rapports, sauvegarde, profil) et les composants partagés. La couche `services/` regroupe la logique métier (authentification, produits, catégories, stock, ventes, achats, clients, fournisseurs, commandes) et le contexte qui assemble stockage, services et dossiers de travail. Les entités sont définies dans `models/` sous forme de dataclasses sérialisables. Les utilitaires (`utils/`) gèrent le stockage JSON thread-safe, la sécurité des mots de passe, la validation, les sauvegardes, les exports et les images. Les données vivent dans `data/`, les médias dans `assets/`, les archives dans `backups/` et les exports dans `reports/`.

## Prérequis

Python 3 doit être installé sur la machine. Un environnement graphique desktop est nécessaire (Windows, macOS ou Linux avec affichage Tk). Les dépendances listées dans `requirements.txt` doivent pouvoir être installées via pip.

## Installation

Placez-vous dans le dossier `StockTN`, créez éventuellement un environnement virtuel Python, puis installez les dépendances :

```bash
cd StockTN
python -m venv .venv
```

Sous Windows :

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

Sous macOS / Linux :

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Aucune configuration externe (fichier `.env`, serveur ou base distante) n’est requise. Au démarrage, `AppContext` crée automatiquement les dossiers `data/`, `backups/`, `reports/` et `assets/` s’ils sont absents. Si les fichiers JSON métier sont vides ou manquants, certains services initialisent des données de démonstration (utilisateurs, catégories, produits, clients, fournisseurs). Les images produits et le logo se placent dans `assets/`. Les montants sont formatés en TND dans l’interface.

## Utilisation

Lancez l’application depuis le dossier `StockTN` :

```bash
python main.py
```

Connectez-vous avec un compte existant. Les comptes de démonstration créés automatiquement lorsque `users.json` est vide sont : `admin` / `admin123` (administrateur), `vendeur` / `vendeur123` (vendeur) et `client` / `client123` (client). Après connexion, naviguez via la barre latérale selon le rôle. La déconnexion revient à l’écran de login. Les rapports générés peuvent être exportés vers le dossier `reports/` ou un emplacement choisi. Les sauvegardes sont gérées depuis le menu Sauvegarde (administrateur).

## API

StockTN Desktop n’expose pas d’API HTTP ni de services réseau. Toute la logique métier est appelée localement par l’interface graphique via les classes du dossier `services/`, qui lisent et écrivent les fichiers JSON du dossier `data/`.

## Base de données

La persistance repose sur des fichiers JSON dans `data/` : `users.json`, `categories.json`, `products.json`, `customers.json`, `suppliers.json`, `stock_movements.json`, `sales.json`, `purchases.json` et `orders.json`. La classe `JsonStorage` assure lecture/écriture avec verrouillage par fichier et écriture atomique (fichier temporaire puis remplacement). Les identifiants sont des entiers incrémentés localement. Les sauvegardes compressent l’ensemble des `*.json` de `data/` dans `backups/` au format ZIP ; une restauration extrait les JSON et crée au préalable une archive `PreRestore_*.zip` de sécurité.

## Tests

Le dépôt ne contient pas de suite de tests automatisés (unitaires, d’intégration ou d’interface). La validation s’effectue manuellement en lançant l’application et en exerçant les parcours selon les rôles (connexion, CRUD métier, ventes, achats, commandes, exports et sauvegarde).

## Sécurité

Les mots de passe sont stockés sous forme de hachage PBKDF2-HMAC-SHA256 (100 000 itérations, sel aléatoire de 16 octets, comparaison en temps constant) via `utils/security.py`. La connexion refuse les comptes inactifs et ne révèle pas si le nom d’utilisateur ou le mot de passe est en cause. Les menus et vues sont filtrés selon le rôle (`admin`, `seller`, `client`). La suppression d’utilisateurs empêche la suppression du dernier compte et exige le maintien d’au moins un administrateur actif. Les données restent locales sur le poste ; aucune transmission réseau n’est implémentée par l’application. Il est recommandé de changer les mots de passe de démonstration en usage réel et de protéger physiquement le dossier `data/`.

## Déploiement

L’application s’exécute en local comme programme Python desktop. Aucun script de build, conteneurisation ou publication serveur n’est fourni dans le projet. Pour un poste de production, installez Python, les dépendances de `requirements.txt`, déployez le dossier `StockTN` (code, `data/`, `assets/`) et lancez `python main.py`. Prévoir des sauvegardes régulières via le module Sauvegarde ou la copie du dossier `data/`.

## Contribution

Les contributions peuvent porter sur la correction de bugs, l’amélioration de l’interface, l’extension des services métier ou l’ajout de tests. Conservez la structure existante (`models/`, `services/`, `ui/`, `utils/`, `data/`) et le style Python du projet. Avant de proposer une modification, vérifiez manuellement les parcours concernés pour chaque rôle. Documentez clairement l’objectif du changement et évitez d’introduire des dépendances non listées dans `requirements.txt` sans justification.
