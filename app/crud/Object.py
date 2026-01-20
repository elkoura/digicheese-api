from sqlalchemy.orm import Session
from app.models.Object import Object
from app.schemas.Object import ObjectCreate

def create_object(db: Session, object_data: ObjectCreate):
    db_object = Object(**object_data.dict())
    db.add(db_object)
    db.commit()
    db.refresh(db_object)
    return db_object

def get_objects(db: Session):
    return db.query(Object).all()

def get_object(db: Session, object_id: int):
    return db.query(Object).filter(Object.id == object_id).first()

def update_object(db: Session, object_id: int, object_data: ObjectCreate):
    db_object = get_object(db, object_id)
    if db_object:
        for key, value in object_data.dict().items():
            setattr(db_object, key, value)
        db.commit()
        db.refresh(db_object)
    return db_object

def delete_object(db: Session, object_id: int):
    db_object = get_object(db, object_id)
    if db_object:
        db.delete(db_object)
        db.commit()
    return db_object
