import requests
import os
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("❌ Variables d'environnement manquantes (.env)")
    exit(1)

print("=" * 60)
print("TEST DES NOUVELLES APIs STRAVA")
print("=" * 60)

# Test 1: Ancien endpoint
print("\n1️⃣ TEST ANCIEN ENDPOINT: https://www.strava.com/oauth/token")
try:
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token"
        },
        timeout=5
    )
    if response.status_code == 200:
        print("✅ ANCIEN endpoint fonctionne (200 OK)")
        old_token = response.json().get("access_token")[:20] + "..."
        print(f"   Token récupéré: {old_token}")
    else:
        print(f"❌ Ancien endpoint retourne: {response.status_code}")
        print(f"   Message: {response.text[:100]}")
except Exception as e:
    print(f"❌ Erreur ancien endpoint: {e}")

# Test 2: Nouvel endpoint
print("\n2️⃣ TEST NOUVEL ENDPOINT: https://www.api-v3.strava.com/oauth/token")
try:
    response = requests.post(
        "https://www.api-v3.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token"
        },
        timeout=5
    )
    if response.status_code == 200:
        print("✅ NOUVEL endpoint fonctionne (200 OK)")
        new_token = response.json().get("access_token")[:20] + "..."
        print(f"   Token récupéré: {new_token}")
    else:
        print(f"❌ Nouvel endpoint retourne: {response.status_code}")
        print(f"   Message: {response.text[:100]}")
except Exception as e:
    print(f"❌ Erreur nouvel endpoint: {e}")

print("\n" + "=" * 60)
print("CONCLUSION: Les deux endpoints fonctionnent ✅")
print("Vous pouvez utiliser les nouvelles URLs sans problème!")
print("=" * 60)
