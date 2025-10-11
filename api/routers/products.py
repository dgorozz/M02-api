from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from api.database import get_db
from api.schemas import ProductCreate, ProductResponse, ProductUpdate
from api.models import Product


# ========== CRUD FUNCTIONS ============

def list_products(db: Session) -> list[Product]:
    products: list[Product] = db.execute(select(Product)).scalars().all()
    return products


def get_product_by_id(db: Session, product_id: int) -> Product:
    product: Product = db.query(Product).filter(Product.id == product_id).first()
    return product


def update_product_by_id(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product: Product = get_product_by_id(db, product_id)
    if not product:
        return

    data = data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(product, key, value)

    return product


# =======================================


class ProductNotFoundException(HTTPException):
    def __init__(self, product_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found")


router = APIRouter(prefix="/products")


@router.get("/", response_model=list[ProductResponse])
def get_products(db = Depends(get_db)):
    products: list[Product] = list_products(db)
    return products


@router.post("/", response_model=ProductResponse)
def add_product(data: ProductCreate, db = Depends(get_db)):
    product: Product = Product(**data.model_dump())
    db.add(product); db.commit(); db.refresh(product);
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product: Product = get_product_by_id(db, product_id)
    if not product:
        raise ProductNotFoundException(product_id)
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = update_product_by_id(db, product_id, data)
    if not product:
        raise ProductNotFoundException(product_id)
    db.commit(); db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product: Product = get_product_by_id(db, product_id)
    if not product:
        raise ProductNotFoundException(product_id)
    db.delete(product); db.commit();
    return