from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Conditionnement(Base):
    __tablename__ = "conditionnements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    nom: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # limites de poids en grammes (ou kg, mais faut choisir un format)
    poids_min: Mapped[float] = mapped_column(Float, nullable=False)
    poids_max: Mapped[float] = mapped_column(Float, nullable=False)

    # prix d'affranchissement selon ce conditionnement
    prix_affranchissement: Mapped[float] = mapped_column(Float, nullable=False)

    commandes = relationship("Commande", back_populates="conditionnement")