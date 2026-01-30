from __future__ import annotations
from pydantic import BaseModel
from app.models.role import RoleName

class RoleBase(BaseModel):
    name: RoleName

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    name: RoleName | None = None

class RoleRead(RoleBase):
    id: int

    model_config = {"from_attributes": True}