from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, Token, UserLogin
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_user,
    decode_token,
    get_user_by_email,
    is_refresh_token_valid,
    save_refresh_token,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Inscrit un nouvel utilisateur."""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user_dict = user_data.model_dump()
    user = create_user(db, user_dict)
    logger.info(f"User registered: {user.email} (ID: {user.id})")
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Authentifie et retourne les tokens."""
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role.value})

    # Create refresh token
    refresh_token_str, jti = create_refresh_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)  # Match settings
    save_refresh_token(db, user.id, jti, expires_at)

    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    return Token(access_token=access_token, refresh_token=refresh_token_str)


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)) -> Token:
    """Rafraîchit un token d'accès à partir d'un refresh token."""
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        jti = payload.get("jti")
        sub = payload.get("sub")
        if not jti or not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        try:
            user_id = int(sub)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Verify token is valid in database
        if not is_refresh_token_valid(db, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or expired",
            )

        # Get user
        from app.services.auth_service import get_user_by_id

        user = get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new access token
        access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role.value})

        logger.info(f"Token refreshed for user: {user.email} (ID: {user.id})")
        return Token(access_token=access_token, refresh_token=request.refresh_token)

    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
        )


@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> UserRead:
    """Retourne les informations de l'utilisateur courant."""
    return UserRead.model_validate(current_user)
