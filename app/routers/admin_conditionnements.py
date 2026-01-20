from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.conditionnement import (
    ConditionnementCreate,
    ConditionnementResponse
)
from app.crud.conditionnement import (
    create_conditionnement,
    get_conditionnements,
    get_conditionnement,
    update_conditionnement,
    delete_conditionnement
)
from app.core.dependencies import get_current_admin

router = APIRouter(
    prefix="/admin/conditionnements",
    tags=["Admin - Conditionnements"]
)

@router.post(
    "/",
    response_model=ConditionnementResponse,
    dependencies=[Depends(get_current_admin)]
)
def create(data: ConditionnementCreate, db: Session = Depends(get_db)):
    return create_conditionnement(db, data)

@router.get(
    "/",
    response_model=List[ConditionnementResponse],
    dependencies=[Depends(get_current_admin)]
)
def list_all(db: Session = Depends(get_db)):
    return get_conditionnements(db)

@router.get(
    "/{conditionnement_id}",
    response_model=ConditionnementResponse,
    dependencies=[Depends(get_current_admin)]
)
def read(conditionnement_id: int, db: Session = Depends(get_db)):
    conditionnement = get_conditionnement(db, conditionnement_id)
    if not conditionnement:
        raise HTTPException(status_code=404, detail="Conditionnement not found")
    return conditionnement

@router.put(
    "/{conditionnement_id}",
    response_model=ConditionnementResponse,
    dependencies=[Depends(get_current_admin)]
)
def update(
    conditionnement_id: int,
    data: ConditionnementCreate,
    db: Session = Depends(get_db)
):
    conditionnement = update_conditionnement(db, conditionnement_id, data)
    if not conditionnement:
        raise HTTPException(status_code=404, detail="Conditionnement not found")
    return conditionnement

@router.delete(
    "/{conditionnement_id}",
    response_model=ConditionnementResponse,
    dependencies=[Depends(get_current_admin)]
)
def delete(conditionnement_id: int, db: Session = Depends(get_db)):
    conditionnement = delete_conditionnement(db, conditionnement_id)
    if not conditionnement:
        raise HTTPException(status_code=404, detail="Conditionnement not found")
    return conditionnement
