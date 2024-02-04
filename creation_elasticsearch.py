from elasticsearch import Elasticsearch
import json
import csv
import os
import nltk
import re
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download([
     "names",
     "stopwords",
     "state_union",
     "twitter_samples",
     "movie_reviews",
     "averaged_perceptron_tagger",
     "vader_lexicon",
     "punkt",
 ])

es = Elasticsearch(hosts = "https://elastic:datascientest@es01:9200",
                 ca_certs="/certs/ca/ca.crt", request_timeout=600)


# Paramètres pour la création de l'index
index_name = 'reviews_per_category_new'
settings = {
    "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 2
    },
    "mappings": {
        "properties": {
            "Entreprise": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "Review": {
                "properties": {
                    "Contenu": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "Date": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "Lieu": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "Nb_Reviews": {
                        "type": "integer"
                    },
                    "Note": {
                        "type": "integer"
                    },
                    "Pseudo": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "Titre": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    }
                }
            }
        }
    }
}

# Check if the index already exists
if es.indices.exists(index=index_name):
    # Delete the index if it exists
    es.indices.delete(index=index_name)
    print(f"Index '{index_name}' already exists and has been deleted.")

# Création de l'index avec les paramètres définis
response = es.indices.create(index=index_name, body=settings)
print(response)





# Lien du dossier de destination des fichiers sources
path = os.getcwd() + "/json"
print(path)
files = os.listdir(path)
cpt = 1
total = 0

# Parcourir chaque fichier dans le répertoire
for file in files:
    if file.endswith('.json'):  # Vérifier si le fichier a l'extension .json
        name = file.split('.json')[0]
        fileCompleted = os.path.join(path, file)
        print(fileCompleted)
        print("On est entrain d'importer le fichier numéro ", cpt, "nommé", name)
        # Opening JSON file
        with open(fileCompleted) as f:
            # returns JSON object as a dictionary
            data = json.load(f)

            # print number of documents in the json
            count = len(data['Entreprise'])
            print("nombre de documents dans le fichier", name, "est ", count)
            total += count
            # index each document
            for each in range(count):
                doc = data['Entreprise'][each]
                doc_json = json.dumps(doc)
                doc_id = name + "_" + str(each)
                res = es.index(index="reviews_per_category_new", id=doc_id, body=doc_json)
                # print(res['result'])

        # Closing file
        cpt += 1

print("nombre de documents total insérés dans l'index reviews_per_category_new est ", total)




#importer un modèle NLTK
sia = SentimentIntensityAnalyzer()

# Nombre de résultats par scroll pour récupérer les IDs
size = 1000  # Modifiez cette valeur selon le nombre de résultats par scroll souhaité
scroll_timeout = '1m'  # Temps d'attente pour le scroll

# Liste pour stocker tous les IDs
all_ids = []

# Requête pour récupérer les IDs de tous les documents
results = es.search(
    index='reviews_per_category_new',
    body={
        "size": size,
        "_source": False,  # Ne récupérer que les IDs, pas les données complètes
        "query": {"match_all": {}}
    },
    scroll=scroll_timeout
)

# Traitement des résultats pour récupérer les IDs
while results['hits']['hits']:
    for hit in results['hits']['hits']:
        doc_id = hit['_id']
        all_ids.append(doc_id)
    
    # Obtenir le prochain lot de résultats avec le scroll_id pour la prochaine itération
    scroll_id = results['_scroll_id']
    results = es.scroll(scroll_id=scroll_id, scroll=scroll_timeout)

# Affichage du nombre total d'IDs récupérés
print(f"Nombre total d'IDs récupérés : {len(all_ids)}")



# Chemin vers le fichier à supprimer
csv_file = "sentiment_analysis.csv"

# Vérifier si le fichier existe avant de le supprimer
if os.path.exists(csv_file):
    os.remove(csv_file)
    print(f"Le fichier {csv_file} a été supprimé avec succès.")
else:
    print(f"Le fichier {csv_file} n'existe pas.")

compteur = 0

# Ouvrir le fichier CSV en mode ajout pour ne pas écraser les données précédentes
with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')

    # Écrire l'en-tête si le fichier est vide
    if file.tell() == 0:
        writer.writerow(['ID', 'Entreprise', 'Contenu', 'Résultat analyse de sentiment'])
    
    # Parcourir tous les IDs pour récupérer et analyser chaque document
    for doc_id in all_ids:
        # Récupérer le document par son ID
        document = es.get(index='reviews_per_category_new', id=doc_id)  
        
        # Vérifier si le document existe
        hit = document['_source']
        doc_id = document['_id']
        company = hit['Entreprise']

        # Vérification de la structure réelle du champ 'Review' et 'Contenu'
        for review in hit['Review']:
            if 'Contenu' in review:
                content = review['Contenu']
                content = re.sub(r'[^A-Za-z0-9\s]', '', content)

                # Analyse de sentiment avec TextBlob
                #analysis = sia.polarity_scores(content)["compound"] 
                sentiment_score = sia.polarity_scores(content)["compound"]

                # Écrire dans le fichier CSV
                writer.writerow([doc_id, company, content, sentiment_score])

                compteur += 1

# Fermeture du fichier CSV
file.close()
print("Analyse de sentiment réalisée")
print(compteur)