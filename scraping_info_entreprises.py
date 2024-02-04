from bs4 import BeautifulSoup as bs
import time
import json
import pandas as pd
import os
import requests


url = "https://www.trustpilot.com/categories"
page = requests.get(url)  
soup = bs(page.content, "lxml")

category = "electronics_technology"
entreprise_data=[]
#for category in categories:
for i in range (1,30):
    url = f"https://www.trustpilot.com/categories/{category}?page={i}"
    print(url)
    response = requests.get(url)
    soup = bs(response.text, "lxml")
    entreprises = soup.find_all("div", class_="paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_wrapper__2JOo2")
    for entreprise in entreprises:
        nom_entreprise = entreprise.find("p", class_="typography_heading-xs__jSwUz typography_appearance-default__AAY17 styles_displayName__GOhL2").text
        domaine = entreprise.find("span", class_="typography_body-s__aY15Q typography_appearance-default__AAY17").text
        lien_info = entreprise.find("a").get('href', '')
        lien = lien_info.split('/')[-1]
        reviews_element = entreprise.find('p', class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_ratingText__yQ5S7')
        
        if reviews_element :
            reviews_text = reviews_element.text
            note = reviews_text.split('|')[0].strip().replace('TrustScore ','')
            note_trustscore =round(float(note), 2)
            temp = reviews_text.split('|')[-1].replace('reviews','').replace('review','').replace(',','')
            nombre_avis=int(temp.replace(' ',''))
            
        else:
            note_trustscore =None
            nombre_avis =0
        entreprise_data.append([category,nom_entreprise,domaine,nombre_avis,note_trustscore,lien])
    time.sleep(3)
df_entreprise = pd.DataFrame(entreprise_data, columns=['categorie','nom','domaine','nombre_avis', 'note_trustscore','lien'])


# Création du fichier entreprise.csv
df_entreprise.to_csv("entreprise.csv", index=False)
print("le fichier entreprise.csv est créé")





# FONCTION POUR RECUPERER LE NB DE PAGE
def nb_pages (url, star):
    # Récupère le nombre de page d'une URL filtrée sur un nombre d'étoile
    url_star = url+"?stars="+str(star)
    response_star = requests.get(url_star)
    soup_star = bs(response_star.text, 'html.parser')
    if (soup_star.find("a", attrs = {'name' :"pagination-button-last"})) is None :
        if (soup_star.find("a", attrs = {'name' :"pagination-button-5"})) is None :
            if (soup_star.find("a", attrs = {'name' :"pagination-button-4"})) is None :
                if (soup_star.find("a", attrs = {'name' :"pagination-button-3"})) is None :
                    if (soup_star.find("a", attrs = {'name' :"pagination-button-2"})) is None :
                        if (soup_star.find("a", attrs = {'name' :"pagination-button-1"})) is None :
                            nb_page = 0
                        else :
                            nb_page = 1
                    else :
                        nb_page = 2
                else :
                    nb_page = 3
            else :
                nb_page = 4
        else :
            nb_page = 5
    else :
        nb_page = int(soup_star.find("a", attrs = {'name' :"pagination-button-last"}).get_text())
    time.sleep(3)
    return nb_page

# FONCTION POUR RECUPERER LES COMMENTAIRES
def recup_review_entreprise (url, categorie):
    #df_review = pd.DataFrame(columns=["Catégorie","Entreprise","Note","Lieu", "Pseudo", "Nb_Review","Date","Titre","Review"])
    entreprise = {}
    entreprise["Entreprise"] = url.rsplit('/', 1)[-1]
    liste_commentaires_entreprise = []
    for etoile in range(1,6):
        nombre_pages = nb_pages(url, etoile)
        print(etoile,"étoiles, pages :",nombre_pages)
        if nombre_pages > 0 :
            for page in range(1,min(nombre_pages+1,6)) :
        
                # Récupère les infos d'une URL en fonction du nombre d'étoile, et du numéro de page
                #categories,entreprises,notes,lieux,pseudos,nbs_review,dates_review,titres_review,textes_review = [],[],[],[],[],[],[],[],[]
                if page == 1 :
                    url_page = url+'?stars='+str(etoile)
                else :
                    url_page = url+'?page='+str(page)+"&stars="+str(etoile)
                print(url_page)
                response = requests.get(url_page)

                soup_response = bs(response.text, 'html.parser')

                reviews_response = soup_response.find_all('div', class_='styles_reviewCardInner__EwDq2')

                for review in reviews_response :
                    commentaire ={}
                    #categories.append(categorie)

                    #entreprises.append(url)

                    #notes.append(etoile)
                    commentaire["Note"] = etoile

                    if review.find(class_="typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_detailsIcon__Fo_ua") is not None :
                        lieu = review.find(class_="typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_detailsIcon__Fo_ua").text.strip()
                        #lieux.append(lieu)
                        commentaire["Lieu"] = lieu 
                    #else :
                        #lieux.append("")

                    if review.find(class_="typography_heading-xxs__QKBS8 typography_appearance-default__AAY17") is not None :
                        pseudo = review.find(class_="typography_heading-xxs__QKBS8 typography_appearance-default__AAY17").text.strip()
                        #pseudos.append(pseudo)
                        commentaire["Pseudo"] = pseudo
                    #else :            
                        #pseudos.append("")

                    if review.find(class_="typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l") is not None :
                        nb_review = int(review.find(class_="typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l").text.strip().split()[0])
                        #nbs_review.append(nb_review)
                        commentaire["Nb_Reviews"] = nb_review
                    #else :            
                        #nbs_review.append("")

                    if review.find('time').get('datetime') is not None :
                        date_review = review.find('time').get('datetime')
                        #dates_review.append(date_review)
                        commentaire["Date"] = date_review
                    #else :            
                        #dates_review.append("")

                    if review.find(class_="typography_heading-s__f7029 typography_appearance-default__AAY17") is not None :
                        titre_review = review.find(class_="typography_heading-s__f7029 typography_appearance-default__AAY17").get_text()
                        #titres_review.append(titre_review)
                        commentaire["Titre"] = titre_review
                    #else :            
                        #titres_review.append("")

                    if review.find(class_="typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn") is not None :
                        texte_review = review.find(class_="typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn").text.strip()
                        #textes_review.append(texte_review)
                        commentaire["Contenu"] = texte_review
                    #else :            
                        #textes_review.append("")

                    #df_page = pd.DataFrame(list(zip(categories, entreprises,notes,lieux,pseudos,nbs_review,dates_review,titres_review,textes_review)), columns=["Catégorie","Entreprise","Note","Lieu", "Pseudo", "Nb_Review","Date","Titre","Review"])
                    liste_commentaires_entreprise.append(commentaire)

                time.sleep(3)
    
    #df_review.reset_index(drop=True, inplace=True)
    entreprise["Review"]=liste_commentaires_entreprise
    return entreprise

# DONNEES CONTENANT LA LISTE DES ENTREPRISES
liste_entreprise = pd.read_csv("entreprise.csv")

#SCRAPING DES COMMENTAIRES EN FONCTION DES ENTREPRISES DU CSV
dossier = "json"
if not os.path.exists(dossier):
    os.makedirs(dossier)
for filename in os.listdir(dossier) :
    if filename.split('.json')[0] not in list(liste_entreprise["lien"]) :
        path=f"./{dossier}/{filename}"
        os.remove(path)
        #print("%s has been removed successfully" %filename)
for index, row in liste_entreprise.iterrows():
    url_entreprise = row["lien"]
    lien=f"./{dossier}/{url_entreprise}.json"
    if not os.path.exists(lien):
        categorie = {} 
        cat = row["categorie"]  # Récupération de la catégorie spécifique pour cette entreprise
        categorie["Catégorie"] = cat
        recup_cat = []
        url_total_entreprise = "https://www.trustpilot.com/review/" + url_entreprise
        print(url_total_entreprise)
        review_entreprise = recup_review_entreprise(url_total_entreprise, cat)
        recup_cat.append(review_entreprise)
        categorie["Entreprise"] = recup_cat
        with open(os.path.join(dossier, f"{url_entreprise}.json"), "w") as f:
            json.dump(categorie, f, indent=2)