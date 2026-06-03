import os
import json
import logging
import datetime
from dotenv import load_dotenv

from myzone_api import MyzoneAPI
from strava_api import StravaAPI
from graph_generator import generate_myzone_graph

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HISTORY_FILE = "sync_history.json"

def load_sync_history():
    """Charge la liste des IDs d'activités déjà synchronisées."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_sync_history(history):
    """Sauvegarde la liste des IDs d'activités synchronisées."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def clean_activity_name(name):
    """Nettoie le nom d'activité Myzone (l'API renvoie '?' au lieu des emojis)."""
    # Mapping mots-clés -> emojis
    emoji_map = {
        "Boxing": "🥊",
        "Ride": "🚴",
        "Athletic": "💪",
        "shape": "🏋️",
        "rpm": "🚴",
        "Run": "🏃",
        "Swim": "🏊",
        "Yoga": "🧘",
        "HIIT": "🔥",
        "Cycling": "🚴",
        "Workout": "💪",
    }
    # Supprime les "?" isolés (résidus d'emojis perdus)
    cleaned = name.replace(" ?", "").replace("?", "").strip()
    # Supprime les "- " en début de chaîne résidus
    while cleaned.startswith("- "):
        cleaned = cleaned[2:].strip()
    
    # Ajoute le bon emoji basé sur les mots-clés
    for keyword, emoji in emoji_map.items():
        if keyword.lower() in cleaned.lower():
            cleaned = f"{emoji} {cleaned}"
            break
    
    return cleaned if cleaned else "💪 Entraînement Myzone"

def format_iso_date(date_str):
    """Convertit '2026-04-01 12:23:18' en '2026-04-01T12:23:18Z'"""
    return date_str.strip().replace(" ", "T") + "Z"

def generate_tcx(activity, graph_data, max_hr, output_file):
    """Génère un fichier TCX valide à partir du graphe MyZone."""
    start_time = format_iso_date(activity.get("date"))
    duration = activity.get("duration_sec", len(graph_data) * 60)
    calories = activity.get("calories", 0)
    
    tcx = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">',
        '  <Activities>',
        '    <Activity Sport="Other">',
        f'      <Id>{start_time}</Id>',
        f'      <Lap StartTime="{start_time}">',
        f'        <TotalTimeSeconds>{duration}</TotalTimeSeconds>',
        f'        <Calories>{calories}</Calories>',
        f'        <MaximumHeartRateBpm><Value>{activity.get("peak_hr", max_hr)}</Value></MaximumHeartRateBpm>',
        '        <Track>'
    ]
    
    for point in graph_data:
        t = point.get("time").replace(" ", "T") + ":00Z"  # 2026-04-17 12:23 -> 2026-04-17T12:23:00Z
        effort = point.get("value", 0)
        hr = int((effort / 100.0) * max_hr)
        
        tcx.append('          <Trackpoint>')
        tcx.append(f'            <Time>{t}</Time>')
        tcx.append(f'            <HeartRateBpm><Value>{hr}</Value></HeartRateBpm>')
        tcx.append('          </Trackpoint>')

    tcx.extend([
        '        </Track>',
        '      </Lap>',
        '    </Activity>',
        '  </Activities>',
        '</TrainingCenterDatabase>'
    ])
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tcx))


def main():
    # 1. Charger les variables d'environnement
    load_dotenv()
    
    myzone_email = os.getenv("MYZONE_EMAIL")
    myzone_password = os.getenv("MYZONE_PASSWORD")
    max_hr = int(os.getenv("MYZONE_MAX_HR", "190"))
    strava_client_id = os.getenv("STRAVA_CLIENT_ID")
    strava_client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    strava_refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")

    if not all([myzone_email, myzone_password, strava_client_id, strava_client_secret, strava_refresh_token]):
        logger.error("Certaines variables d'environnement sont manquantes dans le fichier .env")
        return

    history = load_sync_history()

    # 2. Initialiser et connecter Myzone (TODO: nécessite les vraies URLs)
    myzone = MyzoneAPI(myzone_email, myzone_password)
    myzone.login()
    
    myzone_activities = myzone.get_recent_activities()

    # 3. Initialiser Strava
    strava = StravaAPI(strava_client_id, strava_client_secret, strava_refresh_token)

    # 3.5 Récupérer les activités Strava des 3 dernières semaines pour anti-doublon
    three_weeks_ago = int((datetime.datetime.now() - datetime.timedelta(days=21)).timestamp())
    strava_activities = strava.get_recent_activities(three_weeks_ago)
    
    # Convertir les dates Strava en objets datetime pour comparaison intelligente
    strava_datetimes = []
    for s_act in strava_activities:
        s_date = s_act.get('start_date_local', '')
        try:
            # Format Strava: '2026-04-01T12:27:35Z'
            dt = datetime.datetime.strptime(s_date[:19], "%Y-%m-%dT%H:%M:%S")
            strava_datetimes.append(dt)
        except ValueError:
            pass

    # 4. Synchroniser les nouvelles activités
    for act in myzone_activities:
        act_id = act.get("id")
        
        if act_id in history:
            logger.info(f"Déjà synchronisé (historique). Ignorée: {act.get('title', '')} ({act.get('date', '')[:10]})")
            continue
            
        # Parser la date Myzone (heure locale Paris) : "2026-04-01 12:23:18"
        try:
            mz_dt = datetime.datetime.strptime(act.get("date", "")[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.warning(f"Date Myzone invalide: {act.get('date')}")
            continue
        
        # LOGIQUE ANTI-DOUBLON : tolérance de 30 minutes
        is_duplicate = False
        for s_dt in strava_datetimes:
            diff = abs((mz_dt - s_dt).total_seconds())
            if diff < 1800:  # 30 minutes
                is_duplicate = True
                break
                
        if is_duplicate:
            logger.info(f"Doublon Strava (~{int(diff/60)} min d'écart). Ignorée: {act.get('title', '')} ({act.get('date', '')[:10]})")
            history.append(act_id)
            save_sync_history(history)
            continue

        guid = act.get("guid")
        name = clean_activity_name(act.get("title", "Entraînement Myzone"))
        description = (f"Synchronisé depuis Myzone.\n"
                       f"MEPs: {act.get('meps')} | Calories: {act.get('calories')}\n"
                       f"FC moy: {act.get('avg_hr')} bpm | FC max: {act.get('peak_hr')} bpm\n"
                       f"Effort moyen: {act.get('avg_effort')}")
        
        if guid:
            # Récupère la courbe
            graph = myzone.get_activity_graph(guid)
            if graph and len(graph) > 0:
                logger.info(f"Envoi avec courbe HR ({len(graph)} points) - {name} ({act.get('date', '')[:10]})")
                
                tcx_filename = f"activity_{act_id}.tcx"
                generate_tcx(act, graph, max_hr, tcx_filename)
                
                upload_res = strava.upload_file(tcx_filename, name, description)
                
                if upload_res:
                    history.append(act_id)
                    save_sync_history(history)
                    logger.info(f"  -> OK !")
                else:
                    logger.warning(f"  -> Échec de la synchronisation pour {name} (ne sera pas ajouté à l'historique)")
                
                # Générer l'image du graphe Myzone
                image_dir = os.getenv("IMAGE_DIR", "images")
                os.makedirs(image_dir, exist_ok=True)
                img_path = f"{image_dir}/graph_{act_id}.png"
                try:
                    generate_myzone_graph(graph, img_path)
                    logger.info(f"Image du graphique générée: {img_path}")
                except Exception as e:
                    logger.error(f"Erreur génération image: {e}")

                # Nettoyage fichier TCX
                if os.path.exists(tcx_filename):
                    os.remove(tcx_filename)
            else:
                # FALLBACK : Création d'activité simple sans la courbe HR
                logger.info(f"Envoi simple (sans courbe) - {name} ({act.get('date', '')[:10]})")
                elapsed = act.get("duration_sec", 3600)
                strava_res = strava.create_activity(name, "Crossfit", format_iso_date(act.get('date')), elapsed, description)
                if strava_res:
                    history.append(act_id)
                    save_sync_history(history)
                    logger.info(f"  -> OK !")
                else:
                    logger.warning(f"  -> Échec de la création d'activité pour {name} (ne sera pas ajouté à l'historique)")
        else:
             logger.debug("Pas de GUID pour cette activité.")
        
    logger.info("Fin du script de synchronisation.")

if __name__ == "__main__":
    main()
