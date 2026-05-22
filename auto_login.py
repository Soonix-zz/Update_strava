import os
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def get_myzone_cookie(email, password):
    """
    Utilise Playwright pour se connecter à Myzone et extraire le cookie de session complet.
    """
    logger.info("Démarrage de Playwright pour l'authentification Myzone...")
    try:
        with sync_playwright() as p:
            # Lancement d'un navigateur headless
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            auth_url = "https://auth.myzone.org/authorize?response_type=code&redirect_uri=https://moves.myzone.org/oauth-redirect/&client_id=ClZNiyQcsBVTrEvwYLMmSzzkkpuHCyVrpAqFcRQmxzlatletDkGamKLHvBXPBGNBUsfMWVMGIHdTdvsD&state=PO-PTCNYQFhyeTxO0-0Z8uHJJJnVbEjZlaCc5Sd8Ldg&code_challenge_method=S256&code_challenge=GCIw1nx3yiYnLrALzgDlkEsYceEdDz_6l2pP7o18uMw&scope=openid email profile&audience=ClZNiyQcsBVTrEvwYLMmSzzkkpuHCyVrpAqFcRQmxzlatletDkGamKLHvBXPBGNBUsfMWVMGIHdTdvsD"

            logger.info("Navigation vers la page de connexion...")
            page.goto(auth_url, wait_until="networkidle")

            # Attendre que les champs soient visibles
            page.wait_for_selector('input[name="username"]', timeout=10000)
            
            logger.info("Remplissage des identifiants...")
            page.fill('input[name="username"]', email)
            page.fill('input[name="password"]', password)
            
            # Clic sur le bouton de connexion (il peut avoir un nom ou un type submit)
            logger.info("Validation du formulaire...")
            page.click('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Log In")')

            # Attendre la redirection vers moves.myzone.org ou oauth-redirect
            try:
                page.wait_for_url("**/moves.myzone.org/**", timeout=15000)
            except Exception as e:
                logger.warning(f"La redirection n'a pas été détectée ou a pris trop de temps. URL actuelle : {page.url}")
                # On continue car parfois on est déjà authentifié et les cookies sont présents

            # Extraction des cookies
            cookies = context.cookies()
            cookie_parts = []
            for cookie in cookies:
                cookie_parts.append(f"{cookie['name']}={cookie['value']}")

            cookie_string = "; ".join(cookie_parts)
            
            if cookie_string:
                logger.info("Cookie Myzone extrait avec succès via Playwright !")
                # On pourrait optionnellement mettre à jour le fichier .env ici, mais le mieux est de le retourner
                browser.close()
                return cookie_string
            else:
                logger.error("Aucun cookie récupéré après la tentative de connexion.")
                browser.close()
                return None
    except Exception as e:
        logger.error(f"Erreur Playwright lors de l'authentification : {e}")
        return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    email = os.getenv("MYZONE_EMAIL")
    password = os.getenv("MYZONE_PASSWORD")
    
    if email and password:
        cookie = get_myzone_cookie(email, password)
        if cookie:
            print("Cookie récupéré:", cookie[:50] + "...")
    else:
        print("Veuillez définir MYZONE_EMAIL et MYZONE_PASSWORD dans le .env")
