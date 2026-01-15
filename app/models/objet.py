from __future__ import annotations

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Objet(Base):
    __tablename__ = "objets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    libelle: Mapped[str] = mapped_column(String(255), nullable=False)

    points_requis: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    poids: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False, default=0)

    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)