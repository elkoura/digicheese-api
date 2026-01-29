from __future__ import annotations
import enum
from sqlalchemy import String, Enum
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class RoleName(str, enum.Enum):
    admin = "admin"
    op_colis = "op_colis"
    op_stocks = "op_stocks"


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[RoleName] = mapped_column(Enum(RoleName, name="role_name"), nullable=False, unique=True)