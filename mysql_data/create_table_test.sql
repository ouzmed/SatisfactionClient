use supply_chain;

/*Création de la table entreprise*/

CREATE TABLE IF NOT EXISTS entreprise (
                                categorie varchar(255),
                                nom varchar(255),
                                domaine varchar(255),
                                nombre_avis int,
                                note_trustscore float,
                                lien varchar(255)
                        );

LOAD DATA INFILE "/var/lib/mysql-files/entreprise.csv"
INTO TABLE entreprise 
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

ALTER TABLE  entreprise ADD entreprise_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;


/*Création de la table analyse_sentiment*/

CREATE TABLE IF NOT EXISTS analyse_sentiment (
                                elasticsearch_id varchar(255) NOT NULL,
                                lien varchar(255) NOT NULL,
                                contenu TEXT,
                                score float
                        );

LOAD DATA INFILE "/var/lib/mysql-files/sentiment_analysis.csv"
INTO TABLE analyse_sentiment 
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
