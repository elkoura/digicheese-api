from pydantic import BaseModel


class ConditionnementRead(BaseModel):
    id: int
    nom: str
    poids_min: float
    poids_max: float
    prix_affranchissement: float

    model_config = {"from_attributes": True}