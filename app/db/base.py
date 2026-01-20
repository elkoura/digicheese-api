from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ⚠️ adapte si besoin (mot de passe, nom de la DB)
DATABASE_URL = "mysql+pymysql://root@localhost:3306/digichesse"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
