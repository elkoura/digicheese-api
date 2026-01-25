from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.commande import StatutCommande


class MouvementColis(Base):
    __tablename__ = "mouvements_colis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    date_mouvement: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ancien_statut: Mapped[StatutCommande] = mapped_column(
        Enum(StatutCommande, name="statut_commande"),
        nullable=False,
    )

    nouveau_statut: Mapped[StatutCommande] = mapped_column(
        Enum(StatutCommande, name="statut_commande"),
        nullable=False,
    )

    commande_id: Mapped[int] = mapped_column(ForeignKey("commandes.id"), nullable=False)

    # optionnel : qui a fait l'action (admin / op_colis)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    commande = relationship("Commande", back_populates="mouvements")
    user = relationship("User")