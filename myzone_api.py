import requests
import logging
import os

logger = logging.getLogger(__name__)

class MyzoneAPI:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = requests.Session()
        # TODO: Ajouter les headers si nécessaire pour imiter Chrome
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.is_logged_in = False

    def login(self):
        """Authentification"""
        # 1. Vérifier si on a un cookie dans le .env
        myzone_cookie = os.getenv("MYZONE_COOKIE")
        
        if not myzone_cookie:
            logger.info("Aucun cookie Myzone trouvé. Tentative de récupération via Playwright...")
            try:
                from auto_login import get_myzone_cookie
                myzone_cookie = get_myzone_cookie(self.email, self.password)
            except ImportError:
                logger.error("Le module auto_login.py est introuvable.")
                return False
                
        if myzone_cookie:
            logger.info("Utilisation du cookie de session Myzone.")
            self.session.headers.update({
                'Cookie': myzone_cookie,
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://moves.myzone.org/user/',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            })
            
            # Vérification simple si le cookie est toujours valide
            test_url = "https://moves.myzone.org/sessioncalls/movesbyrange/?start=2024-01-01&end=2024-01-01"
            try:
                res = self.session.get(test_url)
                if res.status_code == 200 and "data" in res.json():
                    self.is_logged_in = True
                    logger.info("Connexion à Myzone validée !")
                    return True
                else:
                    logger.warning("Le cookie actuel semble expiré ou invalide.")
            except Exception as e:
                logger.warning(f"Impossible de vérifier la validité du cookie: {e}")

            # Si on arrive ici, le cookie est invalide, on tente d'en regénérer un nouveau
            logger.info("Régénération d'un nouveau cookie via Playwright...")
            try:
                from auto_login import get_myzone_cookie
                myzone_cookie = get_myzone_cookie(self.email, self.password)
                if myzone_cookie:
                    self.session.headers.update({'Cookie': myzone_cookie})
                    self.is_logged_in = True
                    logger.info("Connexion à Myzone validée avec le nouveau cookie !")
                    return True
            except Exception as e:
                logger.error(f"Erreur lors de la régénération du cookie : {e}")
                
        logger.error("La connexion Myzone a échoué.")
        return False

    def get_recent_activities(self, days=21):
        """Récupère les activités des N derniers jours via l'endpoint movesbyrange."""
        if not self.is_logged_in:
            logger.warning("Veuillez vous connecter d'abord.")
            return []

        import datetime
        end_date = datetime.date.today().strftime("%Y-%m-%d")
        start_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        activities_url = f"https://moves.myzone.org/sessioncalls/movesbyrange/?start={start_date}&end={end_date}"
        
        logger.info(f"Récupération des activités Myzone du {start_date} au {end_date}...")
        try:
            response = self.session.get(activities_url)
            response.raise_for_status()
            res_json = response.json()
            data = res_json.get("data", [])
            
            parsed_activities = []
            
            if isinstance(data, list):
                for item in data:
                    parsed_activities.append({
                        "id": str(item.get("GUID", "mz_unknown")),
                        "guid": item.get("GUID", ""), 
                        "date": item.get("sStart", item.get("isoDate", "")),  # ex: "2026-04-01 12:23:18"
                        "duration_sec": int(item.get("duration", 0)) * 60, # durée en minutes -> secondes
                        "meps": int(item.get("meps", 0)),
                        "calories": int(item.get("calories", 0)),
                        "avg_hr": int(item.get("avgHR", 0)),
                        "peak_hr": int(item.get("peakHR", 0)),
                        "avg_effort": item.get("avgEffort", ""),
                        "title": item.get("activity", "Myzone Workout")
                    })
                logger.info(f"{len(parsed_activities)} activité(s) trouvée(s) sur Myzone.")
            else:
               logger.warning("Structure de donnée Myzone inconnue.")
               logger.debug(f"Données: {res_json}")

            return parsed_activities

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des activités : {e}")
            return []

    def get_activity_graph(self, guid):
        """Récupère la courbe d'effort (movegraph) pour une activité spécifique"""
        if not self.is_logged_in or not guid:
            return []
            
        graph_url = f"https://moves.myzone.org/sessioncalls/movegraph/?guid={guid}"
        logger.info(f"Récupération du graphe pour le GUID {guid}...")
        try:
            res = self.session.get(graph_url)
            res.raise_for_status()
            data = res.json()
            return data.get("graph", [])
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du graphe : {e}")
            return []
