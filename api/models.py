from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Integer, String, Text, Column, ForeignKey, Boolean, DateTime

from api.config import MAX_PRODUCT_NAME_LENGTH


class DecBase(DeclarativeBase):
    pass


class Product(DecBase):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(MAX_PRODUCT_NAME_LENGTH), unique=True, nullable=False)
    price = Column(Integer)

    transactions = relationship("Transaction", back_populates="product")
    slots = relationship("Slot", back_populates="product")


class Slot(DecBase):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(2), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=0)
    capacity = Column(Integer, nullable=False)

    product = relationship("Product", back_populates="slots")


class Transaction(DecBase):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    slot_id = Column(Integer, ForeignKey("slots.id"))
    amount = Column(Integer, nullable=False)
    date = Column(DateTime)

    product = relationship("Product", back_populates="transactions")
    slot = relationship("Slot")