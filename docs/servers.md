# Configuration des serveurs - Digicheese API

## Environnement de développement local

### Prérequis

- Python 3.12+
- PostgreSQL 16+ (ou Docker)
- Docker et Docker Compose (optionnel mais recommandé)

### Installation

1. **Créer un environnement virtuel** :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Linux/Mac
# ou
.venv\Scripts\activate  # Sur Windows
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement** :
Créez un fichier `.env` à la racine du projet :
```env
DATABASE_URL=postgresql+psycopg://digicheese:digicheese@localhost:5433/digicheese
JWT_SECRET_KEY=your-secret-key-minimum-16-characters-long
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Démarrage avec Docker Compose

**Option recommandée** : Utiliser Docker Compose pour démarrer PostgreSQL et l'API ensemble.

```bash
# Démarrer tous les services
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter les services
docker compose down
```

**Note** : Le service `db` écoute sur le port **5433** (au lieu de 5432) pour éviter les conflits avec un PostgreSQL existant.

### Démarrage manuel

1. **Démarrer PostgreSQL** :
```bash
# Avec Docker
docker compose up -d db

# Ou avec un PostgreSQL local
# Assurez-vous que PostgreSQL écoute sur le port 5433
```

2. **Appliquer les migrations** :
```bash
alembic upgrade head
```

3. **Créer un utilisateur admin** (optionnel) :
```bash
python scripts/init_admin.py
```

4. **Démarrer l'API** :
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur `http://localhost:8000`

### Documentation interactive

Une fois l'API démarrée, accédez à :
- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

## Environnement de production

### Variables d'environnement requises

```env
DATABASE_URL=postgresql+psycopg://user:password@host:port/database
JWT_SECRET_KEY=<clé-secrète-forte-minimum-16-caractères>
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
```

### Déploiement avec Docker

1. **Construire l'image** :
```bash
docker build -t digicheese-api .
```

2. **Démarrer le conteneur** :
```bash
docker run -d \
  --name digicheese-api \
  -p 8000:8000 \
  --env-file .env \
  digicheese-api
```

### Déploiement avec Docker Compose

Le fichier `docker-compose.yml` est configuré pour la production. Assurez-vous de :
1. Configurer les variables d'environnement dans `.env`
2. Modifier `JWT_SECRET_KEY` avec une valeur forte
3. Configurer `CORS_ORIGINS` avec les domaines autorisés
4. Désactiver `DEBUG`

```bash
docker compose up -d
```

## Migrations de base de données

### Créer une nouvelle migration

```bash
alembic revision --autogenerate -m "description de la migration"
```

### Appliquer les migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1  # Revenir d'une version
alembic downgrade base  # Revenir au début
```

## Scripts utilitaires

### Créer un utilisateur admin

```bash
python scripts/init_admin.py \
  --email admin@example.com \
  --password securepassword \
  --idUtil ADMIN001 \
  --nomUtil "Administrator"
```

## Vérification de santé

L'endpoint `/api/health` vérifie :
- La connexion à la base de données
- Le statut général de l'API

```bash
curl http://localhost:8000/api/health
```

## Dépannage

### Erreur de connexion à la base de données

1. Vérifiez que PostgreSQL est démarré
2. Vérifiez les credentials dans `.env`
3. Vérifiez que le port est correct (5433 par défaut avec Docker)

### Erreur "JWT_SECRET_KEY too short"

Assurez-vous que `JWT_SECRET_KEY` dans `.env` fait au moins 16 caractères.

### Erreur de migration

Si les migrations échouent :
1. Vérifiez la connexion à la base de données
2. Vérifiez que les modèles sont correctement importés dans `alembic/env.py`
3. Vérifiez les logs : `alembic upgrade head --sql` pour voir le SQL généré
