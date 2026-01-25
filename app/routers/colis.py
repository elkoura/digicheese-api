# app/routers/colis.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_op_colis
from app.db.session import get_db
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.schemas.commande import (
    CommandeCreate, CommandeRead, CommandeUpdate,
    LigneCommandeCreate, LigneCommandeUpdate,
    CommandeStatutUpdate, CommandeSuiviUpdate
)

from app.services import colis_service

router = APIRouter(prefix="/colis", tags=["colis"])


# ==========================================================
# HELPER : construction de la réponse CommandeRead
# ==========================================================
def build_commande_read(db: Session, commande) -> CommandeRead:
    """
    Construit une réponse CommandeRead complète pour Swagger / API.

    Inclut :
    - poids_total calculé
    - affranchissement calculé
    """
    poids_total = colis_service.compute_poids_total(db, commande)
    affranchissement = colis_service.compute_affranchissement(db, commande)

    return CommandeRead.model_validate(
        {
            "id": commande.id,
            "client_id": commande.client_id,
            "adresse_id": commande.adresse_id,
            "statut": commande.statut,
            "num_suivi": commande.num_suivi,
            "commentaire": commande.commentaire,
            "lignes": commande.lignes,
            "poids_total": poids_total,
            "affranchissement": affranchissement,
        }
    )


# ==========================================================
# CLIENTS
# ==========================================================
@router.post("/clients", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Crée un client final.

    Cahier des charges :
    - Gestion des clients : CRUD complet
    """
    return colis_service.create_client(
        db,
        nom=payload.nom,
        prenom=payload.prenom,
        email=payload.email,
        newsletter=payload.newsletter,
    )


@router.get("/clients", response_model=list[ClientRead])
def list_clients(
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Liste des clients.

    Cahier des charges :
    - Visualiser la liste client
    """
    return colis_service.list_clients(db)


@router.get("/clients/{client_id}", response_model=ClientRead)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Fiche client.

    Cahier des charges :
    - Visualiser la fiche client
    """
    client = colis_service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/clients/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Mise à jour d'un client.
    """
    client = colis_service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    data = payload.model_dump(exclude_unset=True)
    return colis_service.update_client(db, client, data)


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Suppression d'un client.
    """
    client = colis_service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    colis_service.delete_client(db, client)
    return None


# ==========================================================
# COMMANDES
# ==========================================================
@router.post("/commandes", response_model=CommandeRead, status_code=status.HTTP_201_CREATED)
def create_commande(
    payload: CommandeCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Crée une commande.

    Cahier des charges :
    - Gestion des commandes (CRUD)
    - Calcul poids total
    """
    try:
        commande = colis_service.create_commande(
            db,
            client_id=payload.client_id,
            adresse_data=payload.adresse.model_dump(),
            commentaire=payload.commentaire,
        )
        return build_commande_read(db, commande)

    except ValueError as e:
        if str(e) == "CLIENT_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Client not found")
        raise HTTPException(status_code=400, detail="Bad request")


@router.get("/commandes", response_model=list[CommandeRead])
def list_commandes(
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Liste des commandes.
    """
    commandes = colis_service.list_commandes(db)
    return [build_commande_read(db, c) for c in commandes]


@router.get("/commandes/{commande_id}", response_model=CommandeRead)
def get_commande(
    commande_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Détail d'une commande.
    """
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    return build_commande_read(db, commande)


@router.put("/commandes/{commande_id}", response_model=CommandeRead)
def update_commande(
    commande_id: int,
    payload: CommandeUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Mise à jour d'une commande (ex: commentaire).
    """
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    data = payload.model_dump(exclude_unset=True)
    commande = colis_service.update_commande(db, commande, data)
    return build_commande_read(db, commande)


@router.put("/commandes/{commande_id}/suivi", response_model=CommandeRead)
def update_suivi(
    commande_id: int,
    payload: CommandeSuiviUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Ajoute / modifie le numéro de suivi.
    """
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    commande = colis_service.update_suivi(db, commande, payload.num_suivi)
    return build_commande_read(db, commande)


@router.put("/commandes/{commande_id}/statut", response_model=CommandeRead)
def update_statut(
    commande_id: int,
    payload: CommandeStatutUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_op_colis),
):
    """
    Change le statut + historise le mouvement.

    Cahier des charges :
    - Historisation des mouvements de colis
    """
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    commande = colis_service.change_statut(db, commande, payload.statut, current_user)
    return build_commande_read(db, commande)


@router.delete("/commandes/{commande_id}", status_code=status.HTTP_200_OK)
def cancel_commande(
    commande_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_op_colis),
):
    """
    Annule une commande (si autorisé).

    Cahier des charges :
    - Gestion commandes (annulation)
    - Respect des règles métier
    """
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    try:
        commande = colis_service.cancel_commande(db, commande, current_user)
        return {"message": "Commande annulée", "commande_id": commande.id, "statut": commande.statut}
    except ValueError as e:
        if str(e) == "CANCEL_NOT_ALLOWED":
            raise HTTPException(status_code=400, detail="Annulation non autorisée pour ce statut")
        raise HTTPException(status_code=400, detail="Bad request")


# ==========================================================
# LIGNES DE COMMANDE
# ==========================================================
@router.post("/commandes/{commande_id}/lignes", response_model=CommandeRead)
def add_ligne(
    commande_id: int,
    payload: LigneCommandeCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Ajoute une ligne à la commande.
    """
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    try:
        commande = colis_service.add_ligne(db, commande, payload.objet_id, payload.quantite)
        return build_commande_read(db, commande)
    except ValueError as e:
        if str(e) == "OBJET_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Objet not found")
        raise HTTPException(status_code=400, detail="Bad request")


@router.put("/commandes/{commande_id}/lignes/{ligne_id}", response_model=CommandeRead)
def update_ligne(
    commande_id: int,
    ligne_id: int,
    payload: LigneCommandeUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Met à jour une quantité d'une ligne.
    """
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    try:
        commande = colis_service.update_ligne(db, commande, ligne_id, payload.quantite)
        return build_commande_read(db, commande)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ligne not found")


@router.delete("/commandes/{commande_id}/lignes/{ligne_id}", response_model=CommandeRead)
def delete_ligne(
    commande_id: int,
    ligne_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    """
    Supprime une ligne de commande.
    """
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    try:
        commande = colis_service.delete_ligne(db, commande, ligne_id)
        return build_commande_read(db, commande)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ligne not found")