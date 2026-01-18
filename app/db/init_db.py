from __future__ import annotations

from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    """Crée toutes les tables SQLAlchemy en base de données."""
    Base.metadata.create_all(bind=engine)