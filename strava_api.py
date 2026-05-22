import requests
import logging

logger = logging.getLogger(__name__)

class StravaAPI:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.base_url = "https://www.strava.com/api/v3"

    def refresh_access_token(self):
        """Renouvelle le token d'accès Strava en utilisant le refresh token."""
        url = "https://www.strava.com/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            logger.info("Renouvellement du token Strava...")
            response = requests.post(url, data=payload)
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data.get("access_token")
            # Le nouveau refresh token est aussi renvoyé. Dans l'idéal il faudrait le sauvegarder (dans le .env)
            # s'il a changé, pour ne jamais le perdre.
            new_refresh_token = data.get("refresh_token")
            if new_refresh_token and new_refresh_token != self.refresh_token:
                logger.info("Un nouveau Refresh Token Strava a été généré (mais pas sauvegardé dans le code actuel).")
                
            logger.info("Token Strava renouvelé avec succès.")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du renouvellement du token Strava : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(e.response.text)
            return False

    def create_activity(self, name, sport_type, start_date_local, elapsed_time, description=""):
        """Crée une nouvelle activité sur Strava"""
        if not self.access_token:
            if not self.refresh_access_token():
                return False

        url = f"{self.base_url}/activities"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        payload = {
            "name": name,
            "sport_type": sport_type, # ex: 'Workout', 'Run', 'Ride'
            "start_date_local": start_date_local, # Format ISO 8601 ex: '2018-02-20T18:02:13Z'
            "elapsed_time": elapsed_time, # En secondes
            "description": description
        }

        try:
            logger.info(f"Création de l'activité '{name}' sur Strava...")
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            logger.info(f"Activité créée avec succès: {response.json().get('id')}")
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'activité Strava : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(e.response.text)
            return None

    def get_recent_activities(self, after_epoch):
        """Récupère les activités Strava récentes pour éviter les doublons."""
        if not self.access_token:
            if not self.refresh_access_token():
                return []

        url = f"{self.base_url}/athlete/activities?after={after_epoch}&per_page=100"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        try:
            logger.info("Récupération des activités récentes sur Strava...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération Strava : {e}")
            return []

    def upload_file(self, file_path, name, description, sport_type="Crossfit"):
        """Uploade un fichier (.tcx, .gpx, .fit) vers Strava"""
        if not self.access_token:
            if not self.refresh_access_token():
                return False

        url = f"{self.base_url}/uploads"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        # Le type de données dépend de l'extension
        data_type = file_path.split('.')[-1]
        
        payload = {
            "name": name,
            "description": description,
            "data_type": data_type,
            "sport_type": sport_type
        }
        
        logger.info(f"Upload du fichier {file_path} vers Strava...")
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path, f)}
                response = requests.post(url, headers=headers, data=payload, files=files)
            
            response.raise_for_status()
            logger.info("Fichier uploadé avec succès ! Il est en cours de traitement par Strava.")
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de l'upload du fichier Strava : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(e.response.text)
            return None
