from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Adresse(Base):
    __tablename__ = "adresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    comp_adresse1: Mapped[str] = mapped_column(String(255), nullable=False)
    comp_adresse2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comp_adresse3: Mapped[str | None] = mapped_column(String(255), nullable=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    commune_id: Mapped[int] = mapped_column(ForeignKey("communes.id"), nullable=False)

    client = relationship("Client", back_populates="adresses")
    commune = relationship("Commune", back_populates="adresses")

    commandes = relationship("Commande", back_populates="adresse")