# Guide de deploiement - DemocratIA

## Prerequis serveur

- **OS** : Ubuntu 22.04 LTS
- **RAM** : 4 Go minimum
- **Stockage** : 20 Go minimum
- **Docker** : 24.0+
- **Docker Compose** : 2.20+
- **Git** : 2.34+

## Installation de Docker

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
```

## Deploiement

### 1. Cloner le depot

```bash
git clone https://github.com/asbjin/democratia.git
cd democratia
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
nano .env
```

Variables a configurer :
```
POSTGRES_USER=democratia
POSTGRES_PASSWORD=<mot_de_passe_fort>
POSTGRES_DB=democratia
DATABASE_URL=postgresql://democratia:<mot_de_passe>@db:5432/democratia
ANTHROPIC_API_KEY=sk-ant-<votre_cle>
VITE_API_URL=https://votre-domaine.fr/api
```

### 3. Lancer les services

```bash
make up
```

Verifier que les services sont actifs :
```bash
make status
make monitor
```

### 4. Initialiser la base de donnees

```bash
make etl
```

Pour charger des donnees de test :
```bash
make seed
```

### 5. Configurer HTTPS

```bash
chmod +x nginx/ssl-setup.sh
sudo ./nginx/ssl-setup.sh votre-domaine.fr
```

Puis mettre a jour `docker-compose.yml` pour utiliser `nginx-ssl.conf` et exposer le port 443.

## Sauvegardes

### Sauvegarde manuelle

```bash
make backup
```

### Sauvegarde automatique (cron)

```bash
crontab -e
# Ajouter :
0 2 * * * cd /chemin/vers/democratia && make backup
```

Les sauvegardes sont stockees dans `/backups/` et les fichiers de plus de 7 jours sont automatiquement supprimes.

## Mise a jour

```bash
cd democratia
git pull origin main
docker compose build
docker compose up -d
```

Si des migrations sont necessaires :
```bash
make migrate
```

## Surveillance

```bash
make monitor     # Verification de sante
make logs        # Logs en temps reel
make status      # Etat des conteneurs
```

## Arret et nettoyage

```bash
make down        # Arret des services (donnees conservees)
make clean       # Arret + suppression des volumes
```

## Ports utilises

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 80, 443 | Reverse proxy |
| Backend | 8000 | API FastAPI |
| Frontend | 3000 | Serveur Vite |
| PostgreSQL | 5432 | Base de donnees |
