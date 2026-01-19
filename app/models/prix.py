from __future__ import annotations
from sqlalchemy import Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Prix(Base):
    __tablename__ = "prix"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    prixobjet: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    objet_id: Mapped[int] = mapped_column(ForeignKey("objets.id"), unique=True, nullable=False)
    objet = relationship("Objet", back_populates="prix")