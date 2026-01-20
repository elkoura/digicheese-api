from sqlalchemy.orm import Session
from app.models.conditionnement import Conditionnement
from app.schemas.conditionnement import ConditionnementCreate

def create_conditionnement(db: Session, data: ConditionnementCreate):
    db_conditionnement = Conditionnement(**data.dict())
    db.add(db_conditionnement)
    db.commit()
    db.refresh(db_conditionnement)
    return db_conditionnement

def get_conditionnements(db: Session):
    return db.query(Conditionnement).all()

def get_conditionnement(db: Session, conditionnement_id: int):
    return (
        db.query(Conditionnement)
        .filter(Conditionnement.id == conditionnement_id)
        .first()
    )

def update_conditionnement(
    db: Session,
    conditionnement_id: int,
    data: ConditionnementCreate
):
    db_conditionnement = get_conditionnement(db, conditionnement_id)
    if not db_conditionnement:
        return None

    for key, value in data.dict().items():
        setattr(db_conditionnement, key, value)

    db.commit()
    db.refresh(db_conditionnement)
    return db_conditionnement

def delete_conditionnement(db: Session, conditionnement_id: int):
    db_conditionnement = get_conditionnement(db, conditionnement_id)
    if not db_conditionnement:
        return None

    db.delete(db_conditionnement)
    db.commit()
    return db_conditionnement
