import os
from dotenv import load_dotenv

# Charge les variables d'environnement (assurez-vous d'avoir rempli le CLIENT_ID dans .env)
load_dotenv()
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")

if not CLIENT_ID or CLIENT_ID == "votre_client_id_strava":
    print("Veuillez d'abord remplir STRAVA_CLIENT_ID dans le fichier .env")
    exit()

print("=== Configuration Initiale de Strava ===")
print("1. Ouvrez ce lien dans votre navigateur web :")
print(f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:write,activity:read_all")
print("\n2. Cliquez sur 'Autoriser'.")
print("3. Vous allez être redirigé vers une page 'localhost' qui affichera une erreur (c'est normal !).")
print("4. Regardez l'URL dans la barre d'adresse de cette page d'erreur. Elle ressemblera à ça :")
print("   http://localhost/exchange_token?state=&code=VOTRE_CODE_AUTORISATION&scope=...")
print("\n5. Copiez la valeur de VOTRE_CODE_AUTORISATION (juste après 'code=' et avant le '&').")

code = input("\nCollez votre code d'autorisation ici : ")

print("\nSuper ! Maintenant, utilisons ce code pour récupérer votre Refresh Token.")
import requests

print("\nRécupération de votre Refresh Token...")
url = "https://www.strava.com/oauth/token"
payload = {
    "client_id": CLIENT_ID,
    "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
    "code": code,
    "grant_type": "authorization_code"
}

try:
    res = requests.post(url, data=payload)
    res.raise_for_status()
    data = res.json()
    refresh_token = data.get("refresh_token")
    print("\n" + "="*50)
    print("SUCCÈS ! Voici votre Refresh Token :")
    print(refresh_token)
    print("="*50)
    print("\nCopiez cette valeur dans votre fichier .env pour la variable STRAVA_REFRESH_TOKEN.")
    print("Vous êtes maintenant prêt à lancer main.py !")
except Exception as e:
    print(f"\nErreur lors de la récupération : {e}")
    if hasattr(e, 'response') and e.response is not None:
         print(e.response.text)

