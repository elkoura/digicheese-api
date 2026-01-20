from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_op_colis
from app.db.session import get_db
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.schemas.commande import CommandeCreate, CommandeRead, CommandeUpdate, LigneCommandeRead, LigneCommandeCreate, LigneCommandeUpdate, CommandeStatutUpdate, CommandeSuiviUpdate
from app.services import colis_service

router = APIRouter(prefix="/colis", tags=["colis"])

@router.post(
    "/clients",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED
)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    return colis_service.create_client(
        db,
        nom=payload.nom,
        prenom=payload.prenom,
        email=payload.email,
        newsletter=payload.newsletter,
    )


@router.get("/clients", response_model=list[ClientRead])
def list_clients(db: Session = Depends(get_db), _=Depends(get_current_op_colis)):
    return colis_service.list_clients(db)


@router.get("/clients/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db), _=Depends(get_current_op_colis)):
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
    client = colis_service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    data = payload.model_dump(exclude_unset=True)
    return colis_service.update_client(db, client, data)


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db), _=Depends(get_current_op_colis)):
    client = colis_service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    colis_service.delete_client(db, client)
    return None

@router.post(
    "/commandes",
    response_model=CommandeRead,
    status_code=status.HTTP_201_CREATED
)
def create_commande(
    payload: CommandeCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    try:
        commande = colis_service.create_commande(
            db,
            client_id=payload.client_id,
            adresse_data=payload.adresse.model_dump(),
            commentaire=payload.commentaire,
        )

        poids_total = colis_service.compute_poids_total(db, commande)

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
                "affranchissement": None,
            }
        )

    except ValueError as e:
        if str(e) == "CLIENT_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Client not found")
        raise HTTPException(status_code=400, detail="Bad request")
    
@router.get("/commandes", response_model=list[CommandeRead])
def list_commandes(db: Session = Depends(get_db), _=Depends(get_current_op_colis)):
    commandes = colis_service.list_commandes(db)

    # On renvoie le poids_total calculé pour chaque commande
    result = []
    for commande in commandes:
        poids_total = colis_service.compute_poids_total(db, commande)
        result.append(
            CommandeRead.model_validate(
                {
                    "id": commande.id,
                    "client_id": commande.client_id,
                    "adresse_id": commande.adresse_id,
                    "statut": commande.statut,
                    "num_suivi": commande.num_suivi,
                    "commentaire": commande.commentaire,
                    "lignes": commande.lignes,
                    "poids_total": poids_total,
                    "affranchissement": None,
                }
            )
        )
    return result


@router.get("/commandes/{commande_id}", response_model=CommandeRead)
def get_commande(commande_id: int, db: Session = Depends(get_db), _=Depends(get_current_op_colis)):
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    poids_total = colis_service.compute_poids_total(db, commande)

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
            "affranchissement": None,
        }
    )

@router.put("/commandes/{commande_id}", response_model=CommandeRead)
def update_commande(
    commande_id: int,
    payload: CommandeUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    data = payload.model_dump(exclude_unset=True)
    commande = colis_service.update_commande(db, commande, data)

    poids_total = colis_service.compute_poids_total(db, commande)

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
            "affranchissement": None,
        }
    )

@router.delete("/commandes/{commande_id}", status_code=status.HTTP_200_OK)
def cancel_commande(
    commande_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    commande = colis_service.cancel_commande(db, commande)

    return {"message": "Commande annulée", "commande_id": commande.id, "statut": commande.statut}

@router.post("/commandes/{commande_id}/lignes", response_model=CommandeRead)
def add_ligne(
    commande_id: int,
    payload: LigneCommandeCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    try:
        commande = colis_service.add_ligne(db, commande, payload.objet_id, payload.quantite)
        poids_total = colis_service.compute_poids_total(db, commande)

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
                "affranchissement": None,
            }
        )
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
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    try:
        commande = colis_service.update_ligne(db, commande, ligne_id, payload.quantite)
        poids_total = colis_service.compute_poids_total(db, commande)

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
                "affranchissement": None,
            }
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Ligne not found")


@router.delete("/commandes/{commande_id}/lignes/{ligne_id}", response_model=CommandeRead)
def delete_ligne(
    commande_id: int,
    ligne_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_op_colis),
):
    commande = colis_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")

    try:
        commande = colis_service.delete_ligne(db, commande, ligne_id)
        poids_total = colis_service.compute_poids_total(db, commande)

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
                "affranchissement": None,
            }
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Ligne not found")