from pydantic import BaseModel

class CommuneBase(BaseModel):
    cp: str
    nom: str
    departement: str

class CommuneCreate(CommuneBase):
    pass

class CommuneUpdate(CommuneBase):
    pass

class CommuneOut(CommuneBase):
    id: int

    class Config:
        orm_mode = True
