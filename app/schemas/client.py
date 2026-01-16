from __future__ import annotations

from pydantic import BaseModel, EmailStr


class ClientCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr 
    newsletter: bool = False


class ClientUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    email: EmailStr | None = None
    newsletter: bool | None = None


class ClientRead(BaseModel):
    id: int
    nom: str
    prenom: str
    email: EmailStr | None
    newsletter: bool

    class Config:
        from_attributes = True