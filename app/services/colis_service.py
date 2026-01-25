# app/services/colis_service.py
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.adresse import Adresse
from app.models.client import Client
from app.models.commande import Commande, StatutCommande
from app.models.detail_commande import DetailCommande
from app.models.objet import Objet

# ✅ À ajouter si tu les as créés
from app.models.conditionnement import Conditionnement
from app.models.mouvement_colis import MouvementColis
from app.models.user import User


# ==========================================================
# CLIENTS
# ==========================================================
def create_client(
    db: Session,
    *,
    nom: str,
    prenom: str,
    email: str | None,
    newsletter: bool
) -> Client:
    """
    Crée un client dans la base de données.

    Rôle :
    - Permet d'enregistrer un nouveau client final (particulier)
    - Sert de base à la création de commandes.

    Retour :
    - Le client créé (avec son id généré).
    """
    client = Client(nom=nom, prenom=prenom, email=email, newsletter=newsletter)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def list_clients(db: Session) -> list[Client]:
    """
    Retourne la liste des clients (ordre décroissant par id).

    Utilité :
    - Afficher la liste client dans l'espace Op-Colis.
    """
    return db.query(Client).order_by(Client.id.desc()).all()


def get_client(db: Session, client_id: int) -> Client | None:
    """
    Retourne un client par son identifiant.

    Retour :
    - Client si trouvé
    - None sinon
    """
    return db.get(Client, client_id)


def update_client(db: Session, client: Client, data: dict) -> Client:
    """
    Met à jour un client existant.

    Paramètres :
    - client : instance SQLAlchemy déjà récupérée
    - data : dictionnaire des champs à modifier

    Retour :
    - Le client mis à jour
    """
    for k, v in data.items():
        setattr(client, k, v)
    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client: Client) -> None:
    """
    Supprime un client.

    Attention :
    - Selon le cahier des charges, tu peux interdire la suppression si
      le client a des commandes existantes.
    """
    db.delete(client)
    db.commit()


# ==========================================================
# COMMANDES
# ==========================================================
def create_commande(
    db: Session,
    *,
    client_id: int,
    adresse_data: dict,
    commentaire: str | None = None
) -> Commande:
    """
    Crée une commande associée à un client + une adresse.

    Étapes :
    1) Vérifie que le client existe
    2) Crée l'adresse (liée au client)
    3) Crée la commande avec statut initial = CREEE
    4) Enregistre un mouvement (historisation)

    Erreurs :
    - CLIENT_NOT_FOUND si client inexistant
    """
    client = db.get(Client, client_id)
    if not client:
        raise ValueError("CLIENT_NOT_FOUND")

    # Création de l'adresse
    adresse = Adresse(
        comp_adresse1=adresse_data["ligne1"],
        comp_adresse2=adresse_data.get("ligne2"),
        comp_adresse3=adresse_data.get("ligne3"),
        commune_id=adresse_data["commune_id"],
        client_id=client.id,
    )
    db.add(adresse)
    db.flush()  # récupère adresse.id

    # Création de la commande
    commande = Commande(
        client_id=client.id,
        adresse_id=adresse.id,
        statut=StatutCommande.CREEE,
        commentaire=commentaire,
    )
    db.add(commande)
    db.flush()  # récupère commande.id

    # Historisation du statut initial
    mouvement = MouvementColis(
        commande_id=commande.id,
        ancien_statut=StatutCommande.CREEE,
        nouveau_statut=StatutCommande.CREEE,
        user_id=None,
    )
    db.add(mouvement)

    db.commit()
    db.refresh(commande)
    return commande


def list_commandes(db: Session) -> list[Commande]:
    """
    Retourne toutes les commandes (ordre décroissant par id).

    Utilité :
    - Visualiser les colis en cours
    - Voir l'historique de commandes
    """
    return db.query(Commande).order_by(Commande.id.desc()).all()


def get_commande(db: Session, commande_id: int) -> Commande | None:
    """
    Retourne une commande par son identifiant.
    """
    return db.get(Commande, commande_id)


def update_commande(db: Session, commande: Commande, data: dict) -> Commande:
    """
    Met à jour les champs modifiables d'une commande.

    Exemple :
    - commentaire
    - adresse (si tu veux l'autoriser, mais souvent l'adresse est figée)
    """
    for k, v in data.items():
        setattr(commande, k, v)
    db.commit()
    db.refresh(commande)
    return commande


def update_suivi(db: Session, commande: Commande, num_suivi: str) -> Commande:
    """
    Met à jour le numéro de suivi.

    Utilité :
    - Quand le colis est pris en charge, on affecte un numéro de tracking.
    """
    commande.num_suivi = num_suivi
    db.commit()
    db.refresh(commande)
    return commande


# ==========================================================
# STATUT + HISTORISATION
# ==========================================================
def can_cancel_commande(commande: Commande) -> bool:
    """
    Règle métier : est-ce qu'on a le droit d'annuler ?

    Exemple de règle :
    - On peut annuler uniquement si la commande est CREEE ou EN_PREPARATION
    - Si elle est DEPOSEE/LIVREE => trop tard
    - Si elle est déjà ANNULEE => inutile

    Tu peux ajuster selon ton cahier des charges.
    """
    return commande.statut in {StatutCommande.CREEE, StatutCommande.EN_PREPARATION}


def change_statut(
    db: Session,
    commande: Commande,
    new_statut: StatutCommande,
    current_user: User | None = None,
) -> Commande:
    """
    Change le statut de la commande et enregistre un mouvement.

    Pourquoi ?
    - Pour historiser chaque changement
    - Pour permettre un suivi complet des colis

    Paramètres :
    - new_statut : le nouveau statut demandé
    - current_user : l'utilisateur connecté (optionnel)
    """
    old_statut = commande.statut
    commande.statut = new_statut

    mouvement = MouvementColis(
        commande_id=commande.id,
        ancien_statut=old_statut,
        nouveau_statut=new_statut,
        user_id=current_user.id if current_user else None,
    )
    db.add(mouvement)

    db.commit()
    db.refresh(commande)
    return commande


def cancel_commande(
    db: Session,
    commande: Commande,
    current_user: User | None = None
) -> Commande:
    """
    Annule une commande selon les règles métier.

    - Vérifie si l'annulation est autorisée
    - Change le statut vers ANNULEE
    - Historise le mouvement

    Erreurs :
    - CANCEL_NOT_ALLOWED si statut interdit
    """
    if not can_cancel_commande(commande):
        raise ValueError("CANCEL_NOT_ALLOWED")

    return change_statut(db, commande, StatutCommande.ANNULEE, current_user)


# ==========================================================
# LIGNES DE COMMANDE
# ==========================================================
def add_ligne(db: Session, commande: Commande, objet_id: int, quantite: int) -> Commande:
    """
    Ajoute une ligne (détail) à une commande.

    Vérification :
    - l'objet existe
    """
    objet = db.get(Objet, objet_id)
    if not objet:
        raise ValueError("OBJET_NOT_FOUND")

    ligne = DetailCommande(
        commande_id=commande.id,
        objet_id=objet.id,
        quantite=quantite
    )
    db.add(ligne)
    db.commit()
    db.refresh(commande)
    return commande


def update_ligne(db: Session, commande: Commande, ligne_id: int, quantite: int) -> Commande:
    """
    Met à jour la quantité d'une ligne.

    Vérification :
    - la ligne existe
    - elle appartient bien à la commande
    """
    ligne = db.get(DetailCommande, ligne_id)
    if not ligne or ligne.commande_id != commande.id:
        raise ValueError("LIGNE_NOT_FOUND")

    ligne.quantite = quantite
    db.commit()
    db.refresh(commande)
    return commande


def delete_ligne(db: Session, commande: Commande, ligne_id: int) -> Commande:
    """
    Supprime une ligne de commande.
    """
    ligne = db.get(DetailCommande, ligne_id)
    if not ligne or ligne.commande_id != commande.id:
        raise ValueError("LIGNE_NOT_FOUND")

    db.delete(ligne)
    db.commit()
    db.refresh(commande)
    return commande


# ==========================================================
# CALCULS : poids + conditionnement + affranchissement
# ==========================================================
def compute_poids_total(db: Session, commande: Commande) -> float:
    """
    Calcule le poids total d'une commande.

    Formule :
    - somme(objet.poids * quantite)
    - + (tare conditionnement) si tu veux l'ajouter plus tard

    Remarque :
    - Si objet.poids est en grammes, le résultat est en grammes.
    """
    total = 0.0
    for ligne in commande.lignes:
        objet = db.get(Objet, ligne.objet_id)
        if objet:
            total += float(objet.poids) * ligne.quantite
    return total


def find_conditionnement(db: Session, poids_total: float) -> Conditionnement | None:
    """
    Trouve le conditionnement adapté au poids total.

    Exemple :
    - 0g → 500g => Carton S
    - 501g → 2000g => Carton M

    Retour :
    - Conditionnement ou None si aucun match
    """
    return (
        db.query(Conditionnement)
        .filter(Conditionnement.poids_min <= poids_total)
        .filter(Conditionnement.poids_max >= poids_total)
        .first()
    )


def compute_affranchissement(db: Session, commande: Commande) -> float | None:
    """
    Calcule l'affranchissement selon le poids total.

    Étapes :
    - calcul poids_total
    - recherche conditionnement
    - renvoie son prix_affranchissement

    Retour :
    - float si trouvé
    - None si aucun conditionnement
    """
    poids_total = compute_poids_total(db, commande)
    cond = find_conditionnement(db, poids_total)
    if not cond:
        return None
    return float(cond.prix_affranchissement)