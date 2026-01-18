from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.commune import CommuneCreate, CommuneUpdate, CommuneOut
from app.crud.commune import (
    get_communes,
    get_commune,
    create_commune,
    update_commune,
    delete_commune
)
from app.core.security import admin_required

router = APIRouter(
    prefix="/admin/communes",
    tags=["Admin - Commune"],
    dependencies=[Depends(admin_required)]
)

@router.get("/", response_model=List[CommuneOut])
def list_communes(db: Session = Depends(get_db)):
    return get_communes(db)

@router.get("/{commune_id}", response_model=CommuneOut)
def read_commune(commune_id: int, db: Session = Depends(get_db)):
    commune = get_commune(db, commune_id)
    if not commune:
        raise HTTPException(status_code=404, detail="Commune non trouvée")
    return commune

@router.post("/", response_model=CommuneOut)
def create(commune: CommuneCreate, db: Session = Depends(get_db)):
    return create_commune(db, commune)

@router.put("/{commune_id}", response_model=CommuneOut)
def update(commune_id: int, commune: CommuneUpdate, db: Session = Depends(get_db)):
    updated = update_commune(db, commune_id, commune)
    if not updated:
        raise HTTPException(status_code=404, detail="Commune non trouvée")
    return updated

@router.delete("/{commune_id}")
def delete(commune_id: int, db: Session = Depends(get_db)):
    deleted = delete_commune(db, commune_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Commune non trouvée")
    return {"message": "Commune supprimée"}
