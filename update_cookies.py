import json
import sys
import os

def update_env_from_cookies(json_path, env_path='.env'):
    """
    Lit un fichier JSON exporté par l'extension Cookie-Edit, 
    extrait les cookies et met à jour la variable MYZONE_COOKIE dans le fichier .env.
    """
    try:
        # Lire le fichier JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            
        # Extraire les cookies
        cookie_parts = []
        for cookie in cookies:
            if 'name' in cookie and 'value' in cookie:
                cookie_parts.append(f"{cookie['name']}={cookie['value']}")
                
        if not cookie_parts:
            print("[ERREUR] Aucun cookie trouvé dans le fichier JSON.")
            return

        # Construire la chaîne de cookies
        cookie_string = "; ".join(cookie_parts)
        print(f"[OK] Chaîne de cookies générée ({len(cookie_parts)} cookies)")
        
        # Lire le contenu actuel du .env
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
            
        # Mettre à jour ou ajouter MYZONE_COOKIE
        cookie_updated = False
        with open(env_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip().startswith('MYZONE_COOKIE') or line.strip().startswith('MYZONE_COOKIE '):
                    f.write(f"MYZONE_COOKIE={cookie_string}\n")
                    cookie_updated = True
                else:
                    f.write(line)
                    
            # Si la variable n'existait pas, on l'ajoute à la fin
            if not cookie_updated:
                if lines and not lines[-1].endswith('\n'):
                    f.write('\n')
                f.write(f"MYZONE_COOKIE={cookie_string}\n")
                
        print(f"[OK] Fichier {env_path} mis à jour avec succès !")
        
    except FileNotFoundError:
        print(f"[ERREUR] Le fichier {json_path} est introuvable.")
    except json.JSONDecodeError:
        print(f"[ERREUR] Le fichier {json_path} n'est pas un JSON valide.")
    except Exception as e:
        print(f"[ERREUR] Une erreur s'est produite : {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
        update_env_from_cookies(json_file_path)
    else:
        print("[INFO] Utilisation : python update_cookies.py <chemin_vers_cookies.json>")
        print("       Exemple     : python update_cookies.py cookies.json")
