from datetime import datetime
from pydantic import BaseModel
from app.models.commande import StatutCommande


class MouvementColisRead(BaseModel):
    id: int
    date_mouvement: datetime
    ancien_statut: StatutCommande
    nouveau_statut: StatutCommande
    commande_id: int
    user_id: int | None

    model_config = {"from_attributes": True}