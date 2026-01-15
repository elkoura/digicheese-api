from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Adresse(Base):
    __tablename__ = "adresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    ligne1: Mapped[str] = mapped_column(String(255), nullable=False)
    ligne2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ligne3: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # FK vers Commune (déjà gérée côté admin)
    commune_id: Mapped[int] = mapped_column(ForeignKey("communes.id"), nullable=False)

    # On relie l'adresse à un client (pratique pour retrouver l'historique)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)

    client = relationship("Client", back_populates="adresses")
    commune = relationship("Commune")