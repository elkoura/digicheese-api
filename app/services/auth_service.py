from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone


import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe en clair contre son hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False




def get_password_hash(password: str) -> str:
    """Hash bcrypt (limite de 72 octets)."""
    # Bcrypt a une limite de 72 octets, on tronque si besoin
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crée un JWT d'accès."""
    to_encode = data.copy()
    # python-jose enforces `sub` to be a string
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(user_id: int) -> tuple[str, str]:
    """Crée un refresh token et retourne (token, jti)."""
    jti = secrets.token_urlsafe(32)
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    # python-jose enforces `sub` to be a string
    to_encode = {"sub": str(user_id), "jti": jti, "exp": expire, "type": "refresh"}
    token = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def decode_token(token: str) -> dict:
    """Décode et valide un JWT."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


def get_user_by_email(db: Session, email: str) -> User | None:
    """Récupère un utilisateur par email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Récupère un utilisateur par id."""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Authentifie un utilisateur via email et mot de passe."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_user(db: Session, user_create: dict) -> User:
    """Crée un nouvel utilisateur."""
    hashed_password = get_password_hash(user_create["password"])

    db_user = User(
        email=user_create["email"],
        idUtil=user_create.get("idUtil"),
        nomUtil=user_create.get("nomUtil"),
        hashed_password=hashed_password,
        role=user_create.get("role", UserRole.op_colis),  # ✅ default op-colis
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def save_refresh_token(db: Session, user_id: int, jti: str, expires_at: datetime) -> RefreshToken:
    """Enregistre un refresh token en base."""
    db_token = RefreshToken(jti=jti, user_id=user_id, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_refresh_token(db: Session, jti: str) -> RefreshToken | None:
    """Récupère un refresh token par jti."""
    return db.query(RefreshToken).filter(RefreshToken.jti == jti).first()


def revoke_refresh_token(db: Session, jti: str) -> None:
    """Révoque un refresh token."""
    token = get_refresh_token(db, jti)
    if token:
        token.revoked = True
        db.commit()


def is_refresh_token_valid(db: Session, jti: str) -> bool:
    """Vérifie si un refresh token est valide (existe, non révoqué, non expiré)."""
    token = get_refresh_token(db, jti)
    if not token:
        return False
    if token.revoked:
        return False

    expires_at = token.expires_at

    # MariaDB/MySQL renvoie souvent un datetime "naive" (sans tzinfo)
    # même si on utilise DateTime(timezone=True). On considère alors que c'est de l'UTC.
    if expires_at is None:
        return False
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        return False

    return True
