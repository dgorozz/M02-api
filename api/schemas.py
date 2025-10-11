from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import string

from api.config import NUM_PRODUCTS_PER_SLOT, NUM_SLOTS_PER_ROW, NUM_ROWS


# =========== PRODUCT ============

class ProductBase(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=20)
    price: Optional[int] = Field(None, gt=0)

class ProductCreate(ProductBase):
    name: str = Field(..., min_length=2, max_length=20)
    price: int = Field(..., gt=0)

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    name: str
    price: int

    class Config:
        orm_mode = True


# =========== SLOT ============

class SlotBase(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = Field(0, ge=0, le=NUM_PRODUCTS_PER_SLOT)

class SlotCreate(SlotBase):
    code: str = Field(..., min_length=2, max_length=2)
    capacity: int = Field(..., gt=0, le=NUM_PRODUCTS_PER_SLOT)

    @field_validator("code")
    def validate_code(value: str):
        if value[0] not in string.ascii_uppercase[:NUM_ROWS]:
            raise ValueError(f"Code must start with an uppercase letter and between A and {string.ascii_uppercase[NUM_ROWS-1]} i.e. 'A2'")
        if value[1] not in string.digits[1:NUM_SLOTS_PER_ROW+1]:
            raise ValueError(f"Code must end with a digit between 1 and {NUM_SLOTS_PER_ROW} i.e. 'B9'")
        return value


class SlotUpdate(SlotBase):
    pass

class SlotResponse(SlotBase):
    id: int
    code: str
    capacity: int

    class Config:
        orm_mode = True


# =========== TRANSACTION ============

class TransactionBase(BaseModel):
    product_id: Optional[int] = Field(None)
    slot_id: Optional[int] = Field(None)
    amount: int = Field(..., gt=0)
    date: datetime = Field(...)

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int

    class Config:
        orm_mode=True


# =========== PAYMENT ============

class PaymentRequest(BaseModel):
    slot: str = Field(..., min_length=2, max_length=2)
    amount: int = Field(..., gt=0)


__all__ = [
    "ProductCreate",
    "ProductUpdate",
    "SlotCreate",
    "SlotUpdate",
    "TransactionCreate"
]