from pydantic import BaseModel

class ConditionnementBase(BaseModel):
    nom: str
    poids_tare: float

class ConditionnementCreate(ConditionnementBase):
    pass

class ConditionnementUpdate(ConditionnementBase):
    pass

class ConditionnementResponse(ConditionnementBase):
    id: int

    class Config:
        orm_mode = True
