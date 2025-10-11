from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.database import get_db
from api.schemas import SlotCreate, SlotUpdate, SlotResponse
from api.models import Slot


# ========== CRUD FUNCTIONS ============

def list_slots(db: Session) -> list[Slot]:
    slots: list[Slot] = db.execute(select(Slot)).scalars().all()
    return slots


def get_slot_by_code(db: Session, code: str) -> Slot:
    slot: Slot = db.query(Slot).filter(Slot.code==code).first()
    return slot


def get_slot_by_id(db: Session, slot_id: int) -> Slot:
    slot: Slot = db.query(Slot).filter(Slot.id == slot_id).first()
    return slot



# =======================================


class SlotNotFoundException(HTTPException):
    def __init__(self, slot_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Slot with ID {slot_id} not found")


router = APIRouter(prefix="/slots")


@router.get("/", response_model=list[SlotResponse])
def get_slots(db = Depends(get_db)):
    slots: list[Slot] = list_slots(db)
    return slots


@router.post("/", response_model=SlotResponse)
def create_slot(data: SlotCreate, db: Session = Depends(get_db)) -> Slot:
    slot: Slot = Slot(**data.model_dump())
    db.add(slot); 
    try:
        db.commit(); db.refresh(slot);
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Slot with code {slot.code} already exists")
    return slot


@router.get("/{slot_id}", response_model=SlotResponse)
def get_slots(slot_id: int, db = Depends(get_db)):
    slot = get_slot_by_id(db, slot_id)

    if not slot:
        raise SlotNotFoundException(slot_id=slot_id)
    
    return slot


@router.patch("/{slot_id}", response_model=SlotResponse)
def update_slot(slot_id: int, data: SlotUpdate, db = Depends(get_db)) -> Slot:
    slot = get_slot_by_id(db, slot_id)

    if not slot:
        raise SlotNotFoundException(slot_id=slot_id)
    
    if not slot.product_id and not data.product_id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Slot has not a product associated and not product_id provided")
    
    if data.product_id:
        slot.product_id = data.product_id
    
    if data.quantity:
        slot.quantity = data.quantity

    db.commit(); db.refresh(slot)

    return slot


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_slot(slot_id: int, db: Session = Depends(get_db)):
    slot: Slot = get_slot_by_id(db, slot_id)
    if not slot:
        raise SlotNotFoundException(slot_id)
    db.delete(slot); db.commit();
    return

