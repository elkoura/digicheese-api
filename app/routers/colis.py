from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.schemas.commande import CommandeCreate, CommandeRead
from app.services import colis_service

router = APIRouter(prefix="/colis", tags=["colis"])


@router.post("/clients", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return colis_service.create_client(
        db,
        nom=payload.nom,
        prenom=payload.prenom,
        email=payload.email,
        newsletter=payload.newsletter,
    )


@router.post("/commandes", response_model=CommandeRead, status_code=status.HTTP_201_CREATED)
def create_commande(payload: CommandeCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    try:
        commande = colis_service.create_commande(
            db,
            client_id=payload.client_id,
            adresse_data=payload.adresse.model_dump(),
            commentaire=payload.commentaire,
        )
        poids_total = colis_service.compute_poids_total(db, commande)

        # Tu construis la réponse
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