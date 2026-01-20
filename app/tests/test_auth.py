"""Tests des endpoints d'authentification."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.services.auth_service import create_user


@pytest.fixture
def test_user(db: Session) -> User:
    """Crée un utilisateur de test."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "idUtil": "TEST001",
        "nomUtil": "Test User",
    }
    return create_user(db, user_data)


def test_register_user(client: TestClient, db: Session) -> None:
    """Inscription d'un utilisateur."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "idUtil": "NEW001",
            "nomUtil": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["idUtil"] == "NEW001"
    assert data["nomUtil"] == "New User"
    assert data["role"] == "op-colis"
    assert "password" not in data


def test_register_duplicate_email(client: TestClient, db: Session, test_user: User) -> None:
    """Inscription avec email déjà utilisé."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client: TestClient, db: Session, test_user: User) -> None:
    """Connexion réussie."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, db: Session, test_user: User) -> None:
    """Connexion avec mauvais identifiants."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_get_current_user(client: TestClient, db: Session, test_user: User) -> None:
    """Récupère l'utilisateur courant."""
    # First login to get token
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id


def test_get_current_user_no_token(client: TestClient) -> None:
    """Appel sans token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401  # FastAPI returns 401 for missing auth


def test_get_current_user_invalid_token(client: TestClient) -> None:
    """Appel avec token invalide."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401


def test_refresh_token(client: TestClient, db: Session, test_user: User) -> None:
    """Rafraîchissement d'un token."""
    # First login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_refresh_token_invalid(client: TestClient) -> None:
    """Rafraîchissement avec token invalide."""
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 401
