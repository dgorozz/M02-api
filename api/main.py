from fastapi import FastAPI, Depends
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
import uvicorn
from sqlalchemy.orm import Session

from datetime import datetime

from api.database import engine, get_db
from api.models import DecBase
import api.models as models
import api.schemas as schemas
from api.routers.products import router as products_router, list_products
from api.routers.slots import router as slots_router, get_slot_by_code, list_slots
from api.routers.transactions import router as transactions_router, list_transactions


app = FastAPI()
app.include_router(products_router)
app.include_router(slots_router)
app.include_router(transactions_router)

DecBase.metadata.create_all(bind=engine)


@app.get("/")
def index():
    return Response({"msg": "This is the MACHINE api"})


@app.get("/info", response_model=schemas.MachineResponse)
def get_info(db: Session = Depends(get_db)):
    products = list_products(db)
    slots = list_slots(db)
    transactions = list_transactions(db)
    return schemas.MachineResponse(
        slots=[schemas.SlotResponse.model_validate(s, from_attributes=True) for s in slots], 
        products=[schemas.ProductResponse.model_validate(p, from_attributes=True) for p in products], 
        transactions=[schemas.TransactionResponse.model_validate(t, from_attributes=True) for t in transactions]
    )


@app.post("/buy")
def buy(data: schemas.PaymentRequest, db: Session = Depends(get_db)):
    slot_code = data.slot
    amount = data.amount

    slot: models.Slot = get_slot_by_code(db, slot_code)

    if not slot:
        raise HTTPException(status_code=404, detail=f"Slot with code {slot_code} not found")

    if not slot.product_id:
        raise HTTPException(status_code=402, detail=f"Slot with no product associated")

    if slot.quantity == 0:
        raise HTTPException(status_code=402, detail=f"Empty slot")
    
    if amount < slot.product.price:
        raise HTTPException(status_code=402, detail=f"Product price is {slot.product.price} and you gave {amount}. Insufficient")
    
    # remove product from slot
    slot.quantity -= 1

    # create transaction
    transaction = models.Transaction(**schemas.TransactionCreate(
        product_id = slot.product_id,
        slot_id=slot.id,
        date=datetime.today(),
        amount=amount
    ).model_dump())

    # apply changes to database
    db.add(transaction); db.commit()
    db.refresh(slot); db.refresh(transaction)

    return transaction


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="localhost", port=8000)