from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from api.database import get_db
from api.schemas import TransactionResponse
from api.models import Transaction


# ========== CRUD FUNCTIONS ============

def list_transactions(db: Session) -> list[Transaction]:
    transactions: list[Transaction] = db.execute(select(Transaction)).scalars().all()
    return transactions


def get_transaction_by_id(db: Session, transaction_id: int) -> Transaction:
    transaction: Transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    return transaction

# =======================================


class TransactionNotFoundException(HTTPException):
    def __init__(self, transaction_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with ID {transaction_id} not found")


router = APIRouter(prefix="/transactions")


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    transactions: list[Transaction] = list_transactions(db)
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction: Transaction = get_transaction_by_id(db, transaction_id)
    
    if not transaction:
        raise TransactionNotFoundException(transaction_id)
    
    return transaction

