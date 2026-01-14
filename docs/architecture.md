# Architecture Digicheese API

## Vue d'ensemble

L'API Digicheese est construite avec **FastAPI** et **PostgreSQL**, suivant une architecture modulaire et organisée.

## Structure du projet

```
digicheese-api/
├── app/
│   ├── core/           # Configuration, logging, dépendances
│   ├── db/             # Session SQLAlchemy, base
│   ├── models/         # Modèles SQLAlchemy (User, RefreshToken)
│   ├── routers/        # Routes FastAPI (auth, health)
│   ├── schemas/        # Schémas Pydantic (validation)
│   ├── services/       # Logique métier (auth_service)
│   └── tests/          # Tests unitaires et d'intégration
├── alembic/            # Migrations de base de données
├── scripts/            # Scripts utilitaires (init_admin.py)
└── docs/               # Documentation
```

## Modules principaux

### 1. Authentification (`app/routers/auth.py`)

**Responsable : Étudiant 1 (Lead Backend)**

Endpoints disponibles :
- `POST /api/auth/register` : Création de compte utilisateur
- `POST /api/auth/login` : Connexion et obtention de tokens JWT
- `POST /api/auth/refresh` : Rafraîchissement du token d'accès
- `GET /api/auth/me` : Informations de l'utilisateur connecté

**Sécurité** :
- Hashage des mots de passe avec bcrypt
- Tokens JWT (access + refresh)
- Gestion des rôles (admin, employee, client)

### 2. Base de données

**Modèle User** (`app/models/user.py`) :
- `id` : Identifiant primaire (auto-incrémenté)
- `idUtil` : Identifiant métier (unique, nullable)
- `nomUtil` : Nom de l'utilisateur (nullable)
- `email` : Email (unique, requis)
- `hashed_password` : Mot de passe hashé
- `is_active` : Statut actif/inactif
- `role` : Rôle (admin, employee, client)
- `created_at`, `updated_at` : Timestamps

**Modèle RefreshToken** (`app/models/refresh_token.py`) :
- `jti` : JWT ID (clé primaire)
- `user_id` : Référence vers User (CASCADE on delete)
- `revoked` : Statut de révocation
- `expires_at` : Date d'expiration
- `created_at` : Date de création

### 3. Services métier

**Auth Service** (`app/services/auth_service.py`) :
- Hashage/vérification de mots de passe
- Génération/validation de tokens JWT
- Gestion des refresh tokens
- CRUD utilisateurs

### 4. Dépendances de sécurité

**Dépendances** (`app/core/dependencies.py`) :
- `get_current_user` : Récupère l'utilisateur depuis le token JWT
- `get_current_admin` : Vérifie le rôle admin
- `get_current_employee` : Vérifie le rôle employee ou admin
- `require_role` : Factory pour vérifier des rôles spécifiques

## Conventions pour les autres étudiants

### Ajout de nouvelles routes

1. Créer un nouveau router dans `app/routers/`
2. L'importer dans `app/routers/__init__.py`
3. L'inclure dans `app/main.py` avec `app.include_router()`

Exemple :
```python
# app/routers/products.py
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
def list_products(current_user: User = Depends(get_current_user)):
    # Votre logique ici
    pass
```

### Protection des routes

- Route publique : Pas de dépendance
- Route authentifiée : `Depends(get_current_user)`
- Route admin uniquement : `Depends(get_current_admin)`
- Route employee/admin : `Depends(get_current_employee)`

### Ajout de nouveaux modèles

1. Créer le modèle dans `app/models/`
2. L'exporter dans `app/models/__init__.py`
3. Créer une migration Alembic : `alembic revision --autogenerate -m "description"`
4. Appliquer : `alembic upgrade head`

### Format des réponses

Toutes les réponses d'erreur suivent le format :
```json
{
  "detail": "Message d'erreur en anglais"
}
```

Les réponses de succès retournent directement les données (pas d'enveloppe JSON).

## Rôles et permissions

- **admin** : Accès complet à toutes les fonctionnalités
- **employee** : Accès aux fonctionnalités de vente/gestion
- **client** : Accès aux fonctionnalités client (catalogue, commandes)

## Base de données

**URL de connexion** : Configurée via `DATABASE_URL` dans `.env`

**Migrations** : Gérées par Alembic
- Créer : `alembic revision --autogenerate -m "message"`
- Appliquer : `alembic upgrade head`
- Rollback : `alembic downgrade -1`

## Configuration

Variables d'environnement (`.env`) :
- `DATABASE_URL` : URL de connexion PostgreSQL
- `JWT_SECRET_KEY` : Clé secrète pour signer les JWT (minimum 16 caractères)
- `JWT_ALGORITHM` : Algorithme JWT (défaut: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` : Durée de vie du token d'accès (défaut: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS` : Durée de vie du refresh token (défaut: 30)
- `CORS_ORIGINS` : Liste des origines autorisées (séparées par des virgules)
- `DEBUG` : Mode debug (true/false)
- `LOG_LEVEL` : Niveau de log (INFO, WARNING, ERROR)
