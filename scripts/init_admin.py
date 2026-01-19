#!/usr/bin/env python3
"""Script pour créer un administrateur par défaut."""

from __future__ import annotations

import sys
from pathlib import Path

# Ajoute le dossier parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.services.auth_service import get_password_hash, get_user_by_email

settings = get_settings()


def create_admin_user(email: str = "admin@digicheese.com", password: str = "admin123", idUtil: str = "ADMIN001", nomUtil: str = "Administrator") -> None:
    """Crée un utilisateur administrateur par défaut."""
    db: Session = SessionLocal()
    try:
        # Vérifie si l'admin existe déjà
        existing = get_user_by_email(db, email)
        if existing:
            print(f"Un admin avec l'email {email} existe déjà.")
            return

        # Création de l'admin
        admin = User(
            email=email,
            idUtil=idUtil,
            nomUtil=nomUtil,
            hashed_password=get_password_hash(password),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin créé :")
        print(f"  Email      : {email}")
        print(f"  ID Util    : {idUtil}")
        print(f"  Nom Util   : {nomUtil}")
        print(f"  Mot de passe: {password} (à changer en production)")
        print(f"  User ID    : {admin.id}")
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la création de l'admin : {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Créer un administrateur par défaut")
    parser.add_argument("--email", default="admin@digicheese.com", help="Email de l'admin")
    parser.add_argument("--password", default="admin123", help="Mot de passe de l'admin")
    parser.add_argument("--idUtil", default="ADMIN001", help="Identifiant métier")
    parser.add_argument("--nomUtil", default="Administrator", help="Nom de l'admin")
    args = parser.parse_args()

    create_admin_user(args.email, args.password, args.idUtil, args.nomUtil)
