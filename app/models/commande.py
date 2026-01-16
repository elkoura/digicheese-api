from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StatutCommande(str, enum.Enum):
    CREEE = "CREEE"
    EN_PREPARATION = "EN_PREPARATION"
    PRETE = "PRETE"
    DEPOSEE = "DEPOSEE"
    LIVREE = "LIVREE"


class Commande(Base):
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    statut: Mapped[StatutCommande] = mapped_column(
        Enum(StatutCommande, name="statut_commande"),
        nullable=False,
        default=StatutCommande.CREEE,
    )

    num_suivi: Mapped[str | None] = mapped_column(String(100), nullable=True)
    commentaire: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    adresse_id: Mapped[int] = mapped_column(ForeignKey("adresses.id"), nullable=False)

    client = relationship("Client", back_populates="commandes")
    adresse = relationship("Adresse", back_populates="commandes")

    lignes = relationship("DetailCommande", back_populates="commande", cascade="all, delete-orphan")