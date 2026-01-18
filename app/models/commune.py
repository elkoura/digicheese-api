from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Commune(Base):
    __tablename__ = "t_commune"

    id = Column(Integer, primary_key=True, index=True)
    cp = Column(String(10), nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    departement = Column(String(100), nullable=False)
