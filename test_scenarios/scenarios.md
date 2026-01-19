# Scénarios de tests manuels - API Digicheese

**Projet** : Refonte SI gestion cadeaux fidélité - Fromagerie DIGICHEES  
**Environnement** : Local (FastAPI + MySQL/MariaDB)  
**Outil principal** : Swagger UI[](http://127.0.0.1:8000/docs)
**Prérequis**  
- Serveur lancé : `uvicorn app.main:app --reload`  
- Fichier `.env` avec `AUTO_CREATE_TABLES=true`  
- Base de données vide au démarrage des tests (tables créées automatiquement par SQLAlchemy au premier lancement)



## 1. Création du premier utilisateur et passage en rôle administrateur.

**Objectif** : Disposer d’un compte administrateur pour tester toutes les fonctionnalités.


### 1.1 Création du premier utilisateur avec rôle par défaut.
**Méthode** : POST  
**Endpoint**: /api/auth/register  
**Payload**: 
{
  "email": "admin@example.com",
  "idUtil": "ADMIN001",
  "nomUtil": "Administrateur principal",
  "password": "ADMIN12345"
}  
**Résultat attendu**: Utilisateur créé avec rôle "Client" par défaut  
**Résultat obtenu**: Code 201 - 
{
  "email": "admin@example.com",
  "idUtil": "ADMIN001",
  "nomUtil": "Administrateur principal",
  "id": 1,
  "is_active": true,
  "role": "client",
  "created_at": "2026-01-19T10:49:09",
  "updated_at": "2026-01-19T10:49:09"
}   

### 1.2 Modification du rôle directement dans la base de données.
**Action** directe sur la base de données - SQL: UPDATE users SET role = 'admin' WHERE idUtil = 'ADMIN001';  
**Résultat attendu**: Rôle modifié en "admin"  
**Vérification**: SELECT idUtil, role FROM users WHERE idUtil = 'ADMIN001';  

***

## 2. Authentification – Connexion administrateur.
**Prérequis**: Utilisateur "admin" créé et rôle modifié en base de données (étape 1).  
**Méthode**: POST  
**Endpoint**: /api/auth/login  
**Payload**:
{
  "email": "admin@example.com",
  "password": "ADMIN12345"
}  
**Résultat attendu**: Authentification réussie et récupération d'un access token et refresh token.  
**Résultat obtenu**: Code 200 - 
{
  "access_token": "ACCESS_TOKEN",
  "refresh_token": "REFRESH_TOKEN",
  "token_type": "bearer"
}  

***

## 3. Tests des droits administrateur.  
**Prérequis**: Authentification d'un admin réussie et récupération de l'access token.  Injection de l'access token dans swagger (Authorize).  

### 3.1 Lister les utilisateurs.  
**Méthode**: GET  
**Endpoint**: /api/admin/users  
**Payload**: aucun paramètre  
**Résultat attendu**: Code 200 - Liste des utilisateurs.  
**Résultat obtenu**: Liste des utilisateurs. 
[
  {
    "email": "admin@example.com",
    "idUtil": "ADMIN001",
    "nomUtil": "Administrateur principal",
    "id": 1,
    "is_active": true,
    "role": "admin",
    "created_at": "2026-01-19T10:49:09",
    "updated_at": "2026-01-19T10:49:09"
  }
]  

### 3.2 Création d'un utilisateur.  
**Méthode**: POST  
**Endpoint**: /api/admin/users  
**Payload**: 
{
  "email": "EMAIL_UTILISATEUR",
  "idUtil": "1",
  "nomUtil": "NOM_UTILISATEUR",
  "password": "PASSWORD_UTILISATEUR"
}  
**Résultat attendu**: Code 201 - Utilisateur créé.  
**Résultat obtenu**: Utilisateur créé avec succès. 
{
  "email": "user1@example.com",
  "idUtil": "1",
  "nomUtil": "user1",
  "id": 2,
  "is_active": true,
  "role": "client",
  "created_at": "2026-01-19T12:37:03",
  "updated_at": "2026-01-19T12:37:03"
}  


### 3.3 Obtenir les détails d'un utilisateur.  
**Méthode**: GET  
**Endpoint**: /api/admin/users/{id}  
**Résultat attendu**: Informations de l'utilisateur selon son identifiant.  
**Résultat obtenu**: 
{
  "email": "admin@example.com",
  "idUtil": "ADMIN001",
  "nomUtil": "Administrateur principal",
  "id": 1,
  "is_active": true,
  "role": "admin",
  "created_at": "2026-01-19T10:49:09",
  "updated_at": "2026-01-19T10:49:09"
}  

### 3.4 Modifier les informations d'un utilisateur.  
**Méthode**: PUT  
**Endpoint**: /api/admin/users/{id}  
**Payload**: 
{
  "email": "EMAIL_UTILISATEUR",
  "idUtil": "ID_UTILISATEUR",
  "nomUtil": "NOM_UTILISATEUR",
  "is_active": true or false
}  
**Résultat attendu**: Code 200 - Informations utilisateur modifiées.  
**Résultat obtenu**: Informations utilisateur modifiées.
{
  "email": "user@example.com",
  "idUtil": "string",
  "nomUtil": "updateUser2",
  "id": 2,
  "is_active": true,
  "role": "client",
  "created_at": "2026-01-19T12:37:03",
  "updated_at": "2026-01-19T13:04:48"
}

### 3.5 Suppression d'un utilisateur.  
**Méthode**: DELETE  
**Endpoint**: /api/admin/users/{id}  
**Résultat attendu**: Code 204 - Suppression de l'utilisateur.  
**Résultat obtenu**: Utilisateur supprimé de la base de données.  
  

***

## Création d'un client en tant qu'Admin.  
**Prérequis**: Authentification d'un admin réussie et récupération de l'access token.  Injection de l'access token dans swagger (Authorize).
**Méthode**: POST  
**Endpoint**: /api/colis/clients  
**Payload**:
{
  "nom": "NOM_CLIENT",
  "prenom": "PRENOM_CLIENT",
  "email": "EMAIL_CLIENT",
  "newsletter": true or false
}  
**Résultat attendu**: Code 201 - Création d'un client.  
**Résultat obtenu**: Client créé. 
{
  "id": 1,
  "nom": "client",
  "prenom": "premier",
  "email": "client1@example.com",
  "newsletter": false
}  
**Vérification**: SQL: SELECT * FROM clients;

***

## Création d'une commande en tant qu'Admin.  
**Prérequis**: Authentification d'un admin réussie et récupération de l'access token.  Injection de l'access token dans swagger (Authorize).  
**Methode**: POST  
**Endpoint**: /api/colis/commandes  
**Payload**:
{
  "client_id": 0,
  "adresse": {
    "ligne1": "string",
    "ligne2": "string",
    "ligne3": "string",
    "commune_id": 0
  },
  "commentaire": "string"
}  
**Résultat attendu**: Code 201 - Commande créée.  
**Résultat obtenu**: ERREUR COMMUNE...  MODIFICATION EN COURS...  

***

