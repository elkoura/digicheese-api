from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.Object import ObjectCreate, ObjectResponse
from app.crud.Object import create_object, get_objects, get_object, update_object, delete_object
router = APIRouter(
    prefix="/admin/objects",
    tags=["Admin - Objects"]
)

@router.post("/", response_model=ObjectResponse)
def create(object_data: ObjectCreate, db: Session = Depends(get_db)):
    return create_object(db, object_data)

@router.get("/", response_model=List[ObjectResponse])
def list_all(db: Session = Depends(get_db)):
    return get_objects(db)
