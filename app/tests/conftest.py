"""Configuration Pytest (PostgreSQL)."""

from __future__ import annotations

from collections.abc import Generator

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Ensure models are imported so Base.metadata is populated.
from app.models import RefreshToken, User  # noqa: F401


def _derive_test_db_url() -> str:
    """
    Utilise TEST_DATABASE_URL si présent, sinon dérive DATABASE_URL
    en remplaçant le nom de base par "<nom>_test".
    """
    settings = get_settings()
    raw = os.getenv("TEST_DATABASE_URL")
    if raw:
        return raw

    url = make_url(str(settings.database_url))
    db_name = url.database or "digicheese"
    return str(url.set(database=f"{db_name}_test"))


TEST_DATABASE_URL = _derive_test_db_url()
test_url = make_url(TEST_DATABASE_URL)

# If a local .env contains a redacted password (e.g. "***"), force the real one for tests.
if test_url.password in (None, "", "***"):
    # Prefer explicit env, fallback to docker-compose defaults.
    test_url = test_url.set(password=os.getenv("POSTGRES_PASSWORD", "digicheese"))


def _admin_url_for_create_db(url: URL) -> URL:
    # Postgres impose CREATE DATABASE depuis une autre base (souvent "postgres")
    return url.set(database="postgres")


admin_engine = create_engine(_admin_url_for_create_db(test_url), isolation_level="AUTOCOMMIT")
engine = create_engine(test_url, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_test_database_exists() -> None:
    db_name = test_url.database
    if not db_name:
        raise RuntimeError("Test database name is missing in TEST_DATABASE_URL")

    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))


@pytest.fixture(scope="session", autouse=True)
def _setup_test_db_schema() -> Generator[None, None, None]:
    """
    Crée la base de test si besoin et le schéma (une fois par session).
    Les données sont nettoyées entre tests via TRUNCATE.
    """
    _ensure_test_database_exists()
    Base.metadata.create_all(bind=engine)
    yield
    # Keep DB for faster local runs; schema cleanup is optional.


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Ouvre une session de test et nettoie les données entre tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        # Clean all data (keep schema) for isolation.
        session.execute(text("TRUNCATE TABLE refresh_tokens, users RESTART IDENTITY CASCADE"))
        session.commit()
        session.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Client de test branché sur la session DB de test."""
    app.dependency_overrides[get_db] = lambda: db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
