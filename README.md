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

Le dépôt contient 2 Dockerfiles : un pour builder l'image d'un container qui se lancera en https, et l'autre en http (indifférent en local)

**Pour développer dans le container en https :**

```
git clone https://github.com/azur-scd/koha-primo-middleware.git
docker build -t -f Dockerfile_https azurscd/koha-primo-middleware:latest .
docker run -d --name koha-primo-middleware -p 5000:5000 -v <your_local_path>/koha-primo-middleware:/app azurscd/koha-primo-middleware:latest

```
Tourne en local sur https://localhost:5000/koha-primo-middleware (ex : [https://localhost:5000/koha-primo-middleware/api/v1/hello](https://localhost:5000/api/v1/hello))

**Pour développer dans le container en http :**

```
git clone https://github.com/azur-scd/koha-primo-middleware.git
docker build -t -f Dockerfile_http azurscd/koha-primo-middleware:dev-http
docker run -d --name koha-primo-middleware -p 5000:5000 -v <your_local_path>/koha-primo-middleware:/app azurscd/koha-primo-middleware:dev-http

```
Tourne en local sur http://localhost:5000/koha-primo-middleware (ex : [http://localhost:5000/koha-primo-middleware/api/v1/hello](http://localhost:5000/api/v1/hello))


### Intégration locale avec [https://github.com/azur-scd/koha-primo-explore-devenv](https://github.com/azur-scd/koha-primo-explore-devenv)

#### Lancer la vue UCA dans primo-explore en suivant les instructions du README du dépôt (peut tourner sous node.js local ou dans un container)

#### Pour binder primo-explore sur le container local koha-primo-middleware

Dans le dossier du projet koha-primo-explore-devenv, ouvrir /primo-explore/custom/UCA/js/main.js et paramétrer le provider KOHA_MIDDLEWARE_URL sur la valeur adéquate de l'objet URLs.

> **_NOTE:_**  Ne pas oublier de remettre la valeur de KOHA_MIDDLEWARE_URL._api sur URLs._prodscd_koha_primo_middleware avant de builder le nouveau package Primo

## Déploiement en production

Une fois les développements stabilisés dans le conteneur local :

- fichier secrets.env à créer sur le serveur de production à la racine du dossier home de l'utilisateur avec 2 variables : API_KOHA_CLIENT_ID et API_KOHA_CLIENT_SECRET. Attention, pas de guillemets doubles autour des valeurs (contrairement à un .env habituel)
Ex : 
API_KOHA_CLIENT_ID=fake
API_KOHA_CLIENT_SECRET=fake

- ne pas oublier de rebuilder l'image (commande : docker build -t -f Dockerfile_https azurscd/koha-primo-middleware:latest .) 
- pusher sur le dépôt Docker Hub [https://hub.docker.com/repository/docker/azurscd/koha-primo-middleware](https://hub.docker.com/repository/docker/azurscd/koha-primo-middleware)
- déployer sur le serveur de production par un pull de Docker Hub et lancer le conteneur
- la commande docker run doit contenir les arguments suivants : sudo docker run --env-file ./secrets.env -d -it --name koha-primo-middleware -p 5000:5000 azurscd/koha-primo-middleware:latest


### A noter CI/CD via Github Action désactivé

## Todo

Doc Swagger

## Derniers updates


- [x] Due date en format français



