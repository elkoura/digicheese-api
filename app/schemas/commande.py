from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.commande import StatutCommande


class AdresseCreate(BaseModel):
    ligne1: str
    ligne2: str | None = None
    ligne3: str | None = None
    commune_id: int


class CommandeCreate(BaseModel):
    client_id: int
    adresse: AdresseCreate
    commentaire: str | None = None


class CommandeUpdate(BaseModel):
    commentaire: str | None = None


class CommandeStatutUpdate(BaseModel):
    statut: StatutCommande


class CommandeSuiviUpdate(BaseModel):
    num_suivi: str = Field(min_length=5, max_length=100)


class LigneCommandeCreate(BaseModel):
    objet_id: int
    quantite: int = Field(ge=1)


class LigneCommandeUpdate(BaseModel):
    quantite: int = Field(ge=1)


class LigneCommandeRead(BaseModel):
    id: int
    objet_id: int
    quantite: int

    class Config:
        from_attributes = True


class CommandeRead(BaseModel):
    id: int
    client_id: int
    adresse_id: int
    statut: StatutCommande
    num_suivi: str | None
    commentaire: str | None
    lignes: list[LigneCommandeRead] = []

    poids_total: float = 0.0  # calculé côté API
    affranchissement: float | None = None  # placeholder

    class Config:
        from_attributes = True