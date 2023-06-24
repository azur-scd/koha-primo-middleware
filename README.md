# Environnement de développement Primo-Koha : Middleware APIs Koha

![forthebadge](forthebadge.svg)

Container à déployer sur un serveur jouant le rôle de serveur mandataire entre Koha et des applications tierces.

## Objectif

- Pouvoir requêter les API Koha depuis un client (l'UI Angular de Primo en l'occurence) en "outrepassant" les contraintes CORS côté Koha par une requête serveur intermédiaire qui redirige les données en sortie vers le client
- Pouvoir manipuler les données Koha au passage afin de les rendre plus simples à parser côté client / ou les enrichir à la volée

## Cas d'usage

- APIs publiques : header Access-Control-Allow-Origin vide par défaut dans Koha
- APIs privées : gestion d'Oauth2 et gestion du token déportée côté serveur
  
## Routing API Koha

- /api/v1 : Hello World
- /api/v1/hello : Hello World
- /api/v1/koha/biblios_items/{biblio_id} : exemplaires d'une notice bib identifiée par son biblio_id
- /api/v1/koha/items/external_id/{cb} : données d'exemplaires par requête sur le CB


## Développement : Build & déploiement

### Container local

```
git clone https://github.com/azur-scd/koha-primo-middleware.git
docker build -t azurscd/koha-primo-middleware:dev .
docker run -d --name koha-primo-middleware -p 5000:5000 -v <your_local_path>/koha-primo-middleware:/app azurscd/koha-primo-middleware:dev

```
Tourne en local sur https://localhost:5000/koha-primo-middleware (ex : [https://localhost:5000/koha-primo-middleware/api/v1/hello](https://localhost:5000/api/v1/hello))

### Intégration locale avec [https://github.com/azur-scd/koha-primo-explore-devenv](https://github.com/azur-scd/koha-primo-explore-devenv)

#### Lancer la vue UCA dans primo-explore en suivant les instructions du README du dépôt (peut tourner sous node.js local ou dans un container)

#### Pour binder primo-explore sur le container local koha-primo-middleware

Dans le dossier du projet koha-primo-explore-devenv, ouvrir /primo-explore/custom/UCA/js/main.js et paramétrer le provider KOHA_MIDDLEWARE_URL sur la valeur adéquate de l'objet URLs.

> **_NOTE:_**  Ne pas oublier de remettre la valeur de KOHA_MIDDLEWARE_URL._api sur URLs._prodscd_koha_primo_middleware avant de builder le nouveau package Primo

## Déploiement en production

Une fois les développements stabilisés dans le conteneur local :

- ne pas oublier de rebuilder l'image
- pusher sur le dépôt Docker Hub [https://hub.docker.com/repository/docker/azurscd/koha-primo-middleware](https://hub.docker.com/repository/docker/azurscd/koha-primo-middleware)
- déployer en dev sur dev-scd.unice.fr ([http://dev-scd.unice.fr/koha-primo-middleware/api/v1/hello](http://dev-scd.unice.fr/koha-primo-middleware/api/v1/hello) par un pull de Docker Hub
- déployer sur le serveur de production par un pull de Docker Hub

### A noter CI/CD via Github Action désactivé

## Todo

Doc Swagger

## Derniers updates


- [x] Due date en format français



