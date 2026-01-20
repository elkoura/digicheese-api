from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base

class Conditionnement(Base):
    __tablename__ = "t_conditionnement"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    poids_tare = Column(Float, nullable=False)
