# 🏃‍♂️ Update_Strava (Myzone to Strava Sync)

Ce projet permet de synchroniser **automatiquement** vos activités [Myzone](https://www.myzone.org/) vers [Strava](https://www.strava.com/). 

Contrairement à la synchronisation basique proposée par Myzone, ce script :
- Exporte la courbe de fréquence cardiaque complète.
- Génère un fichier `.tcx` valide et l'envoie sur Strava.
- Génère une image (`.png`) du graphique de l'effort Myzone.
- Gère automatiquement les connexions bloquées par Myzone grâce à un navigateur robotisé (Playwright).
- Tourne de façon 100% autonome sur **GitHub Actions**.

---

## ⚙️ Variables d'Environnement

Pour que le script fonctionne (en local ou sur GitHub), il a besoin de connaître vos identifiants. Vous devez créer un fichier `.env` à la racine du projet ou ajouter ces variables dans les **Secrets** de votre dépôt GitHub :

```env
MYZONE_EMAIL=votre_email_myzone@example.com
MYZONE_PASSWORD=votre_mot_de_passe
MYZONE_MAX_HR=190

STRAVA_CLIENT_ID=12345
STRAVA_CLIENT_SECRET=votre_secret_strava
STRAVA_REFRESH_TOKEN=votre_refresh_token_strava
```

> **Note :** Le script `setup_strava.py` peut vous aider à générer facilement votre premier `STRAVA_REFRESH_TOKEN`.

---

## 💻 Utilisation en Local (Sur votre PC)

### 1. Installation des dépendances
Assurez-vous d'avoir Python installé, puis exécutez les commandes suivantes dans votre terminal :

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Lancer la synchronisation
Une fois le fichier `.env` bien rempli :

```bash
python main.py
```
Le script va :
1. Se connecter à Myzone (en ouvrant un navigateur invisible si besoin).
2. Vérifier les activités des 3 dernières semaines sur Strava pour éviter les doublons.
3. Télécharger les nouvelles activités Myzone, créer les `.tcx` et les images.
4. Mettre à jour le fichier de base de données locale `sync_history.json`.

---

## ☁️ Déploiement Automatique (GitHub Actions)

Ce projet est configuré pour s'exécuter **tout seul, gratuitement, tous les jours à 20h00** via GitHub Actions.

Pour l'activer :
1. Poussez ce code sur un dépôt privé GitHub.
2. Allez dans les paramètres de votre dépôt : **Settings > Secrets and variables > Actions**.
3. Ajoutez-y toutes les variables d'environnement listées plus haut (`MYZONE_EMAIL`, etc.) en tant que "Repository secrets".
4. C'est tout ! L'action va se lancer selon le cycle programmé dans `.github/workflows/sync.yml`. 

> GitHub sauvegardera automatiquement le fichier `sync_history.json` directement sur le dépôt pour mémoriser les activités déjà envoyées.

---

## 🛠️ Scripts Annexes

- `setup_strava.py` : Un petit assistant pour vous authentifier sur l'API Strava la toute première fois et obtenir vos jetons d'accès.
- `generate_old_images.py` : Permet de générer uniquement les graphiques `.png` de vos anciennes activités Myzone sans les envoyer sur Strava.
- `auto_login.py` : Le module qui gère le contournement de l'authentification Myzone via Playwright.
