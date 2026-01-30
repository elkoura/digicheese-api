from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole
from app.models.role import RoleName
from typing import List

class UserBase(BaseModel):
    email: EmailStr
    idUtil: str | None = None
    nomUtil: str | None = None
    roles: List[RoleName] = []


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    @Field_validator('roles')
    @classmethod
    def validate_roles(cls, v):
        if not v:
            raise ValueError('Au moins un rôle est nécessaire')
        return v

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    idUtil: str | None = None
    nomUtil: str | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8, description="Le mot de passe doit contenir au moins 8 caractères")
    roles: List[RoleName] | None = None


class UserRead(UserBase):
    id: int
    is_active: bool
    roles: List[RoleName]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserInDB(UserRead):
    hashed_password: str
