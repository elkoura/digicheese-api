"""Configuration Pytest (MySQL/MariaDB)."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db

# Ensure models are imported so Base.metadata is populated.
from app.models import RefreshToken, User  # noqa: F401
import app.models  # noqa: F401


# -------------------------
# 1) Charger .env très tôt
# -------------------------
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH, override=True)


def _derive_test_db_url() -> str:
    """
    Utilise TEST_DATABASE_URL si présent, sinon dérive DATABASE_URL
    en remplaçant le nom de base par "<nom>_test".
    """
    raw = os.getenv("TEST_DATABASE_URL")
    if raw:
        return raw

    settings = get_settings()
    url = make_url(str(settings.database_url))
    db_name = url.database or "digicheese"
    return str(url.set(database=f"{db_name}_test"))


TEST_DATABASE_URL = _derive_test_db_url()
test_url = make_url(TEST_DATABASE_URL)

# IMPORTANT:
# Forcer l'app à utiliser la DB de test PENDANT pytest
os.environ["DATABASE_URL"] = str(test_url)


def _admin_url_for_create_db(url: URL) -> URL:
    """
    En MySQL/MariaDB, on peut CREATE DATABASE en étant connecté à une DB système.
    """
    return url.set(database="mysql")  # ou "information_schema"


admin_engine = create_engine(_admin_url_for_create_db(test_url), isolation_level="AUTOCOMMIT")
engine = create_engine(test_url, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_test_database_exists() -> None:
    db_name = test_url.database
    if not db_name:
        raise RuntimeError("Test database name is missing in TEST_DATABASE_URL")

    with admin_engine.connect() as conn:
        exists = conn.execute(
            text(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                "WHERE SCHEMA_NAME = :name"
            ),
            {"name": db_name},
        ).scalar()

        if not exists:
            conn.execute(text(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))


def _truncate_all_tables(session: Session) -> None:
    session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

    # Tables réellement présentes dans la base
    existing = {
        row[0]
        for row in session.execute(text("SHOW TABLES")).all()
    }

    for table in reversed(Base.metadata.sorted_tables):
        if table.name in existing:
            session.execute(text(f"TRUNCATE TABLE `{table.name}`"))

    session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

@pytest.fixture(scope="session", autouse=True)
def _setup_test_db_schema() -> Generator[None, None, None]:
    """
    Crée la base de test si besoin et le schéma (une fois par session).
    """
    _ensure_test_database_exists()
    Base.metadata.create_all(bind=engine)
    yield
    # Optionnel: ne pas dropper pour accélérer les runs locaux


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        _truncate_all_tables(session)
        session.commit()
        session.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    IMPORTANT : importer app.main ici (après avoir forcé DATABASE_URL)
    """
    from app.main import app  # import tardif exprès

    app.dependency_overrides[get_db] = lambda: db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()