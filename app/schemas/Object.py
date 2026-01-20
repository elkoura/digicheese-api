from pydantic import BaseModel, ConfigDict

class ObjectBase(BaseModel):
    code: str
    libelle: str
    actif: bool = True

class ObjectCreate(ObjectBase):
    pass

class ObjectResponse(ObjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
