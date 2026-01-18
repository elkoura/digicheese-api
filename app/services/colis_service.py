# app/services/colis_service.py
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.adresse import Adresse
from app.models.client import Client
from app.models.commande import Commande, StatutCommande
from app.models.detail_commande import DetailCommande
from app.models.objet import Objet


# ----------------------------
# CLIENTS
# ----------------------------
def create_client(db: Session, *, nom: str, prenom: str, email: str | None, newsletter: bool) -> Client:
    client = Client(nom=nom, prenom=prenom, email=email, newsletter=newsletter)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def list_clients(db: Session) -> list[Client]:
    return db.query(Client).order_by(Client.id.desc()).all()


def get_client(db: Session, client_id: int) -> Client | None:
    return db.get(Client, client_id)


def update_client(db: Session, client: Client, data: dict) -> Client:
    for k, v in data.items():
        setattr(client, k, v)
    db.commit()
    db.refresh(client)
    return client


# ----------------------------
# COMMANDES
# ----------------------------
def create_commande(
    db: Session,
    *,
    client_id: int,
    adresse_data: dict,
    commentaire: str | None = None
) -> Commande:
    client = db.get(Client, client_id)
    if not client:
        raise ValueError("CLIENT_NOT_FOUND")

    adresse = Adresse(
    comp_adresse1=adresse_data["ligne1"],
    comp_adresse2=adresse_data.get("ligne2"),
    comp_adresse3=adresse_data.get("ligne3"),
    commune_id=adresse_data["commune_id"],
    client_id=client.id,
)
    db.add(adresse)
    db.flush()  # récupère adresse.id

    commande = Commande(
        client_id=client.id,
        adresse_id=adresse.id,
        statut=StatutCommande.CREEE,
        commentaire=commentaire,
    )
    db.add(commande)
    db.commit()
    db.refresh(commande)
    return commande


def list_commandes(db: Session) -> list[Commande]:
    return db.query(Commande).order_by(Commande.id.desc()).all()


def get_commande(db: Session, commande_id: int) -> Commande | None:
    return db.get(Commande, commande_id)


def update_commande(db: Session, commande: Commande, data: dict) -> Commande:
    for k, v in data.items():
        setattr(commande, k, v)
    db.commit()
    db.refresh(commande)
    return commande


def update_statut(db: Session, commande: Commande, statut: StatutCommande) -> Commande:
    commande.statut = statut
    db.commit()
    db.refresh(commande)
    return commande


def update_suivi(db: Session, commande: Commande, num_suivi: str) -> Commande:
    commande.num_suivi = num_suivi
    db.commit()
    db.refresh(commande)
    return commande


# ----------------------------
# LIGNES
# ----------------------------
def add_ligne(db: Session, commande: Commande, objet_id: int, quantite: int) -> Commande:
    objet = db.get(Objet, objet_id)
    if not objet:
        raise ValueError("OBJET_NOT_FOUND")

    ligne = DetailCommande(commande_id=commande.id, objet_id=objet.id, quantite=quantite)
    db.add(ligne)
    db.commit()
    db.refresh(commande)
    return commande


def update_ligne(db: Session, commande: Commande, ligne_id: int, quantite: int) -> Commande:
    ligne = db.get(DetailCommande, ligne_id)
    if not ligne or ligne.commande_id != commande.id:
        raise ValueError("LIGNE_NOT_FOUND")

    ligne.quantite = quantite
    db.commit()
    db.refresh(commande)
    return commande


def delete_ligne(db: Session, commande: Commande, ligne_id: int) -> Commande:
    ligne = db.get(DetailCommande, ligne_id)
    if not ligne or ligne.commande_id != commande.id:
        raise ValueError("LIGNE_NOT_FOUND")

    db.delete(ligne)
    db.commit()
    db.refresh(commande)
    return commande


# ----------------------------
# CALCULS
# ----------------------------
def compute_poids_total(db: Session, commande: Commande) -> float:
    total = 0.0
    for ligne in commande.lignes:
        objet = db.get(Objet, ligne.objet_id)
        if objet:
            total += float(objet.poids) * ligne.quantite

    # Conditionnement pas encore implémenté => tare = 0.0
    poids_tare = 0.0
    return total + poids_tare