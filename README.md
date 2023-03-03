# Environnement de développement Primo-Koha : Middleware APIs Koha

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
- /api/v1/koha/biblios_items/{biblio_id} : exemplaires d'une notice bib identifiée par son biblio_id


## Dev : Build & déploiement

### En local

```
git clone https://github.com/azur-scd/koha-primo-middleware.git
docker build -t azurscd/koha-primo-middleware:dev .
docker run -d --name koha-primo-middleware -p 5002:5000 -v <your_local_path>/koha-primo-middleware:/app azurscd/koha-primo-middleware:dev

```
Tourne en local sur https://localhost:5000/koha-primo-middleware (ex : [https://localhost:5000/koha-primo-middleware/api/v1/hello](https://localhost:5000/api/v1/hello))

### CI/CD

Chaque commit/push sur Github déclenche une Github Action qui rebuild et push l'image sur Docker Hub.

## Prod

Dépôt Docker Hub : [https://hub.docker.com/repository/docker/azurscd/koha-primo-middleware](https://hub.docker.com/repository/docker/azurscd/koha-primo-middleware)

Déployé en prod-test sur dev-scd.unice.fr (ex : [http://dev-scd.unice.fr/koha-primo-middleware/api/v1/hello](http://dev-scd.unice.fr/koha-primo-middleware/api/v1/hello)

## Documentation

Doc Swagger



