# app/models/commune.py
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Commune(Base):
    __tablename__ = "communes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cp: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    departement: Mapped[str | None] = mapped_column(String(50), nullable=True)