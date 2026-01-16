from __future__ import annotations

from app.db.base import Base  # noqa: F401

# ⚠️ IMPORTANT : importer tous les models ici
# sinon SQLAlchemy ne les enregistre pas et create_all() ne créera rien.
from app.models.user import User  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401

# Plus tard tu ajouteras :
# from app.models.client import Client  # noqa: F401
# from app.models.commande import Commande  # noqa: F401
# from app.models.adresse import Adresse  # noqa: F401
# from app.models.detail_commande import DetailCommande  # noqa: F401