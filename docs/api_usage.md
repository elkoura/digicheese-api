# Guide d'utilisation de l'API Digicheese

## Base URL

- **Local** : `http://localhost:8000`
- **API Prefix** : `/api`

## Authentification

L'API utilise l'authentification **JWT Bearer Token**. Toutes les requêtes authentifiées doivent inclure le header :
```
Authorization: Bearer <access_token>
```

## Endpoints d'authentification

### 1. Inscription (`POST /api/auth/register`)

Crée un nouveau compte utilisateur.

**Request Body** :
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "idUtil": "USER001",
  "nomUtil": "John Doe"
}
```

**Response** (201 Created) :
```json
{
  "id": 1,
  "email": "user@example.com",
  "idUtil": "USER001",
  "nomUtil": "John Doe",
  "is_active": true,
  "role": "client",
  "created_at": "2026-01-14T14:00:00Z",
  "updated_at": "2026-01-14T14:00:00Z"
}
```

**Erreurs possibles** :
- `400 Bad Request` : Email déjà enregistré
- `422 Unprocessable Entity` : Données invalides

### 2. Connexion (`POST /api/auth/login`)

Authentifie un utilisateur et retourne les tokens JWT.

**Request Body** :
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK) :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Erreurs possibles** :
- `401 Unauthorized` : Email ou mot de passe incorrect

### 3. Rafraîchir le token (`POST /api/auth/refresh`)

Obtient un nouveau token d'accès à partir d'un refresh token.

**Request Body** :
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK) :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Erreurs possibles** :
- `401 Unauthorized` : Refresh token invalide ou expiré

### 4. Informations utilisateur (`GET /api/auth/me`)

Retourne les informations de l'utilisateur connecté.

**Headers** :
```
Authorization: Bearer <access_token>
```

**Response** (200 OK) :
```json
{
  "id": 1,
  "email": "user@example.com",
  "idUtil": "USER001",
  "nomUtil": "John Doe",
  "is_active": true,
  "role": "client",
  "created_at": "2026-01-14T14:00:00Z",
  "updated_at": "2026-01-14T14:00:00Z"
}
```

**Erreurs possibles** :
- `401 Unauthorized` : Token manquant ou invalide
- `403 Forbidden` : Utilisateur inactif

## Health Check

### Vérifier le statut (`GET /api/health`)

Vérifie que l'API et la base de données sont opérationnelles.

**Response** (200 OK) :
```json
{
  "status": "ok"
}
```

## Exemples d'utilisation avec cURL

### Inscription
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "idUtil": "TEST001",
    "nomUtil": "Test User"
  }'
```

### Connexion
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Obtenir les informations utilisateur
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Gestion des erreurs

Toutes les erreurs suivent le format standard :
```json
{
  "detail": "Message d'erreur descriptif"
}
```

**Codes HTTP courants** :
- `200 OK` : Succès
- `201 Created` : Ressource créée
- `400 Bad Request` : Requête invalide
- `401 Unauthorized` : Authentification requise ou échouée
- `403 Forbidden` : Permissions insuffisantes
- `404 Not Found` : Ressource introuvable
- `422 Unprocessable Entity` : Erreur de validation
- `500 Internal Server Error` : Erreur serveur

## Notes importantes

1. **Tokens JWT** : Les tokens d'accès expirent après 30 minutes par défaut. Utilisez le refresh token pour obtenir un nouveau token d'accès.

2. **Mots de passe** : Minimum 8 caractères requis lors de l'inscription.

3. **Rôles** : Les utilisateurs sont créés avec le rôle `client` par défaut. Seul un admin peut modifier les rôles.

4. **Sécurité** : En production, assurez-vous de :
   - Utiliser HTTPS
   - Configurer un `JWT_SECRET_KEY` fort et unique
   - Limiter les origines CORS aux domaines autorisés
