from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class DetailCommande(Base):
    __tablename__ = "detail_commandes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    quantite: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    colis: Mapped[str | None] = mapped_column(String(50), nullable=True)
    commentaire: Mapped[str | None] = mapped_column(String(255), nullable=True)

    commande_id: Mapped[int] = mapped_column(ForeignKey("commandes.id"), nullable=False)
    objet_id: Mapped[int] = mapped_column(ForeignKey("objets.id"), nullable=False)

    commande = relationship("Commande", back_populates="lignes")
    objet = relationship("Objet", back_populates="lignes_commande")