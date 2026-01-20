from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class Object(Base):
    __tablename__ = "t_object"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    actif = Column(Boolean, default=True)
