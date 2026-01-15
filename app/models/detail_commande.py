from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DetailCommande(Base):
    __tablename__ = "detail_commandes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id", ondelete="CASCADE"),
        nullable=False
    )
    objet_id: Mapped[int] = mapped_column(ForeignKey("objets.id"), nullable=False)

    quantite: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    commande = relationship("Commande", back_populates="lignes")
    objet = relationship("Objet")