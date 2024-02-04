import mysql.connector
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
from fastapi import Path
import os

app = FastAPI(title="Satisfaction Client Project - API",
    description="Our API powered by FastAPI. ©️ MMM",
    version="1.0.1")

# Configuration de la base de données
config = {
    'host': "db", #db à la place de localhost
    'port': 3306, #ajout port
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
    'database': os.environ.get('MYSQL_DATABASE'),
    'auth_plugin': 'mysql_native_password',  # Utilisez 'mysql_native_password' au lieu de 'caching_sha2_password'
}

# Exemple de dictionnaire pour les identifiants

# Chargement des variables d'environnement
USER1_PASSWORD = os.environ.get('USER1_PASSWORD')
USER2_PASSWORD = os.environ.get('USER2_PASSWORD')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Utilisateurs
users = {
    "user1": USER1_PASSWORD,
    "user2": USER2_PASSWORD,
    "admin": ADMIN_PASSWORD
} 

# Création de l'objet de connexion à la base de données
def get_database_connection():
    return mysql.connector.connect(**config)

# Sécurité basique avec FastAPI
security = HTTPBasic()

# Fonction pour vérifier les identifiants
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    user_password = users.get(credentials.username)
    if user_password is None or user_password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username

# Point de terminaison pour vérifier si l'API est fonctionnelle
@app.get('/api/status', name ="Statut de l'API")
def get_status():
    return {'status': 'API est fonctionnelle'}

# Endpoint pour récupérer la liste des catégories
'''
@app.get("/categories", response_model=List[str], name = "Liste des catégories disponibles")
async def get_categories(user: str = Depends(verify_credentials)):
    try:
        with get_database_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = "SELECT nom FROM categorie"
                cursor.execute(query)
                categories = cursor.fetchall()
                # Extraire les valeurs de la clé 'nom' de chaque dictionnaire
                category_names = [category['nom'] for category in categories]
                return category_names
    except Exception as e:
        # Gérer les erreurs de connexion ou d'exécution de requête
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données: {e}")
'''
###########
###########

# Endpoint pour récupérer la liste des entreprises pour une catégorie spécifique:

@app.get("/electronics_technology/entreprises", response_model=List[str], name ="Liste des entreprises appartenants à cette catégorie")
async def get_entreprises_for_categorie(*,user: str = Depends(verify_credentials)):
    try:
        with get_database_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT nom FROM entreprise 
                """
                cursor.execute(query)
                entreprises = cursor.fetchall()
                entreprises_names = [entreprise['nom'] for entreprise in entreprises]
                
                if not entreprises_names:
                    raise HTTPException(status_code=404, detail="Aucune entreprise trouvée pour cette catégorie")
                return entreprises_names
    except Exception as e:
        # Gérer les erreurs de connexion ou d'exécution de requête
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données: {e}")

####
####

# Endpoint pour récupérer le nombre de commentaires et la note trsuscore par entreprise en fonction du lien
@app.get("/nombre-de-avis-par-entreprise/{lien}", response_model=dict, name = "nombre d'avis par entreprise")
async def get_avis_number(*,user: str = Depends(verify_credentials), lien: str = Path(..., title="Nom de l'entreprise")):
    try:
        with get_database_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT nombre_avis, note_trustscore
                    FROM entreprise
                    WHERE lien = %s
                """
                cursor.execute(query, (lien,))
                result = cursor.fetchone()

                if result is None:
                    raise HTTPException(status_code=404, detail="Aucune information trouvée pour cette entreprise")
                
                nombre_avis = result.get("nombre_avis")
                note_trustscore = result.get("note_trustscore")

                if nombre_avis is None:
                    raise HTTPException(status_code=404, detail="Pas d'avis trouvés pour cette entreprise")
                if note_trustscore is None:
                    raise HTTPException(status_code=404, detail="Aucune note trouvée pour cette entreprise")
                return {"lien": lien, "nombre_avis": nombre_avis, "note_trustscore": note_trustscore}
    except Exception as e:
        # Gérer les erreurs de connexion ou d'exécution de requête
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données: {e}")
#####
#####

# Endpoint pour récupérer le score moyen par entreprise en fonction du lien
@app.get("/score-moyen-par-entreprise/{lien}", response_model=dict, name = "score moyen de l'analyse de sentiment (>0: positif;<0: négatif)")
async def get_score_moyen_par_entreprise(*,user: str = Depends(verify_credentials), lien: str = Path(..., title="Nom de l'entreprise")):
    try:
        with get_database_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT AVG(score) as score_moyen
                    FROM analyse_sentiment
                    WHERE lien = %s
                """
                cursor.execute(query, (lien,))
                score_moyen = cursor.fetchone()

                if score_moyen is None:
                    raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour cette entreprise")

                return {"lien": lien, "score_moyen": score_moyen["score_moyen"]}
    
    except Exception as e:
        # Gérer les erreurs de connexion ou d'exécution de requête
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données: {e}")
