# Instruction de depart

Chat BJ is a conversational agent designed to facilitate access to public and private e-services by providing factual and concise information on the steps to follow when requesting a service online.

A- To launch the application, follow these steps:
### 1- Create a pyth runtime environment
python -m venv `envname`. - Connect to the env `envname`\Scripts\activate.bat

### 2- Install the dependencies in the requirements.txt file 
pip install -r requirements.txt

### 3- Add the env file to the root directory

### 4- launch the application 
uvicorn main:app --port `port` --reload

### 5- Access to api documentation 
http://localhost:`port`/docs

# Details des differents stages

## Événements de déclenchement :

Le workflow est déclenché lors de tout push ou pull_request sur la branche main.
Job build-and-deploy : Ce job s'exécute sur un runner Ubuntu (version la plus récente).

## Stage 1 : Checkout du code :

- **actions/checkout@v3** : Cette étape permet de récupérer le code source de ton repository sur le runner pour l'utiliser dans les étapes suivantes.

## Stage 2 : Configuration de Docker Buildx :

- **docker/setup-buildx-action@v2** : Configure Docker Buildx. Cela permet de créer des images Docker de manière plus flexible et puissante, notamment avec la possibilité de supporter plusieurs architectures.
  
## Stage 3 : Connexion à Docker Hub :

- **docker/login-action@v2** : Cette étape se connecte à Docker Hub en utilisant les identifiants stockés dans les secrets GitHub (`DOCKER_USERNAME et DOCKER_PASSWORD`). Cela permet de pousser les images Docker vers ton dépôt public sur `docker Hub`.

## Stage 4 : Construction et push de l'image Docker :

- **docker/build-push-action@v3** : Cette étape construit l'image Docker à partir du contexte actuel (le répertoire de travail) et la pousse sur Docker Hub avec deux tags : latest et un tag basé sur le commit actuel (hash de github.sha).
  
## Stage 5 : Déploiement sur OVHcloud via SSH :

- **appleboy/ssh-action@master** : Cette action permet de se connecter à un serveur distant via SSH (`OVHcloud`) et d'y exécuter un script.
Le script fait :
  - **Se connecte à Docker Hub avec les secrets.**
  - **Tire la dernière image Docker construite.**
  - **Crée un fichier chat.db si nécessaire.**
  - **Arrête et supprime un container Docker existant s'il est présent.**
  - **Lance un nouveau container avec la dernière image Docker.**

## Test du deploiement
  Apres le deploiement on test l'API au niveau du navigateur avec l'IP du serveur et le port de connexion puis on accede a l'agent AI avec Swagger-FastAPI  
