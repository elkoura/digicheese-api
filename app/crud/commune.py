from sqlalchemy.orm import Session
from app.models.commune import Commune
from app.schemas.commune import CommuneCreate, CommuneUpdate

def get_communes(db: Session):
    return db.query(Commune).all()

def get_commune(db: Session, commune_id: int):
    return db.query(Commune).filter(Commune.id == commune_id).first()

def create_commune(db: Session, commune: CommuneCreate):
    db_commune = Commune(**commune.dict())
    db.add(db_commune)
    db.commit()
    db.refresh(db_commune)
    return db_commune

def update_commune(db: Session, commune_id: int, commune: CommuneUpdate):
    db_commune = get_commune(db, commune_id)
    if not db_commune:
        return None

    for key, value in commune.dict().items():
        setattr(db_commune, key, value)

    db.commit()
    db.refresh(db_commune)
    return db_commune

def delete_commune(db: Session, commune_id: int):
    db_commune = get_commune(db, commune_id)
    if not db_commune:
        return None

    db.delete(db_commune)
    db.commit()
    return db_commune
