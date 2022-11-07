# Middleware APIs Koha

![forthebadge](forthebadge.svg)

Container à déployer sur un serveur jouant le rôle de serveur mandataire entre Koha et des applications tierces.

## Objectif

- Pouvoir requêter les API Koha depuis un client (l'UI Angular de Primo en l'occurence) en "outrepassant" les contraintes CORS côté Koha par une requête serveur intermédiaire qui redirige les données en sortie vers le client
- Pouvoir manipuler les données Koha au passage afin de les rendre plus simples à parser côté client / ou les enrichir à la volée

## Cas d'usage

- APIs publiques : header Access-Control-Allow-Origin vide par défaut dans Koha

## Routing API Koha

- /api/v1 : Hello World
- /api/v1/hello : Hello World
- /api/v1/koha_items/{biblio_id} : exemplaires d'une notice bib identifiée par son biblio_id


## Dev : Build & déploiement

### En local

```
docker build -t azurscd/koha-primo-middleware:latest .
docker run -d --name koha-primo-middleware -p 5002:5000 -v <your_local_path>/koha-primo-middleware:/app azurscd/koha-primo-middleware:latest

```
Tourne en local sur http://localhost:5002/koha-primo-middleware (ex : [http://localhost:5002/koha-primo-middleware/api/v1/hello](http://localhost:5002/api/v1/hello))

### CI/CD

Chaque commit/push sur Github déclenche une Github Action qui rebuild et push l'image sur Docker Hub.

## Prod

Dépôt Docker Hub : 

Déployé en prod sur dev-scd.unice.fr ()

## Documentation

Doc Swagger



