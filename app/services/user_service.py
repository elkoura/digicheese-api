from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.models.role import Role, RoleName
from app.models.user_role import UserRole
from app.services.auth_service import get_password_hash, get_user_by_email

class UserService:

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        user = db.get(User, user_id)
        if user:
            db.refresh(user, attribute_names=["user_roles"])
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        user = get_user_by_email(User, email)
        if user:
            db.refresh(user, attribute_names=["user_roles"])
        return user

    @staticmethod
    def list_users(db: Session) -> List[User]:
        users = db.execute(select(User).order_by(User.id.desc())).scalars().all()

        for user in users:
            db.refresh(user, attribute_names=["user_roles"])
        return list(users)

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        existing_user = get_user_by_email(db, user_data["email"])
        if existing_user:
            raise ValueError("Cet email existe déjà")

        if not user_data.get("roles"):
            raise ValueError("Aucun rôle spécifié")

        hashed_password = get_password_hash(user_data["password"])

        db_user = User(
            email = user_data["email"],
            idUtil = user_data.get["idUtil"],
            nomUtil = user_data.get["nomUtil"],
            hashed_password = hashed_password
        )

        db.add(db_user)
        db.flush()

        for role_name in user_data["roles"]:
            role = db.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()

            if not role:
                role = Role(name = role_name)
                db.add(role)
                db.flush()

            user_role = UserRole(user_id = db_user.id, role_id=role.id)
            db.add(user_role)

        db.commit()
        db.refresh(db_user)
        db.refresh(db_user, attribute_names=["user_roles"])
        return db_user

        @staticmethod
        def update_user(db: session, user_id: int, update_data: dict) -> User:
            user = db.get(User, user_id)
            if not user:
                raise ValueError("Utilisateur non trouvé")

            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

            if "roles" in update_data:
                db.execute(select(UserRole).where(UserRole.user_id == user.id)).scalars().delete(synchronize_session=False)

                for role_name in update_data["roles"]:
                    role = db.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()

                    if not role:
                        role = Role(name=role_name)
                        db.add(role)
                        db.flush()

                    user_role = UserRole(user_id=user.id, role_id=role.id)
                    db.add(user_role)

                del update_data["roles"]

            for key, value in update_data.items():
                setattr(user, key, value)

            db.commit()
            db.refresh(user)
            db.refresh(user, attribute_names=["user_roles"])

        @staticmethod
        def delete_user(db: Session, user_id: int) -> bool:
            user = db.get(User, user_id)
            if not user:
                raise ValueError("Utilisateur non trouvé")

            db.delete(user)
            db.commit()
            return True

        @staticmethod
        def list_roles(db: Session) -> List[Role]:
            return db.execute(select(Role).order_by(Role.id)).scalars().all()

user_service = UserService()