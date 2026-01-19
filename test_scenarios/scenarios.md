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

NON IMPLEMENTE...  

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

