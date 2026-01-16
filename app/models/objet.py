from __future__ import annotations
from sqlalchemy import Integer, String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Objet(Base):
    __tablename__ = "objets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    libelle: Mapped[str] = mapped_column(String(255), nullable=False)

    taille: Mapped[str | None] = mapped_column(String(50), nullable=True)
    poids: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    indispo: Mapped[bool] = mapped_column(Boolean, default=False)

    lignes_commande = relationship("DetailCommande", back_populates="objet")
    prix = relationship("Prix", back_populates="objet", uselist=False)