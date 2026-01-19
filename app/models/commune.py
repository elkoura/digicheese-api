from __future__ import annotations
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Commune(Base):
    __tablename__ = "communes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cp: Mapped[str] = mapped_column(String(10), nullable=False)
    commune: Mapped[str] = mapped_column(String(255), nullable=False)
    departement: Mapped[str] = mapped_column(String(255), nullable=False)

    adresses = relationship("Adresse", back_populates="commune")