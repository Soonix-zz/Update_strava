import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
from myzone_api import MyzoneAPI
from graph_generator import generate_myzone_graph

myzone = MyzoneAPI(os.getenv('MYZONE_EMAIL'), os.getenv('MYZONE_PASSWORD'))
myzone.login()

acts = myzone.get_recent_activities(days=30)
print(f'Trouvé {len(acts)} activités. Génération des images...')

image_dir = os.getenv("IMAGE_DIR", "images")
os.makedirs(image_dir, exist_ok=True)

for act in acts:
    guid = act.get('guid')
    title = act.get('title', 'Unknown').replace('?','').strip()
    name = ''.join([c for c in title if c.isalnum() or c.isspace()]).replace(' ', '_')
    if guid:
        graph = myzone.get_activity_graph(guid)
        if graph and len(graph) > 0:
            date_str = act.get("date", "2026-01-01")[:10]
            path = f'{image_dir}/{date_str}_{name.strip("_")}.png'
            generate_myzone_graph(graph, path)
            print(f' - OK: {path}')
