from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from api.models import Slot
from api.schemas import SlotCreate
from .test_products import _add_product_to_db


def _add_slot_to_db(session, code: str, capacity: int, quantity: int | None = None, product_id: int | None = None):
    product = Slot(**SlotCreate(code=code, capacity=capacity, quantity=quantity, product_id=product_id).model_dump())
    session.add(product)
    session.commit()
    return product


def test_create_valid_slot(session: Session, client: TestClient):

    slot_with_only_required_data = {"code": "A1", "capacity": 3}
    response = client.post("/slots", json=slot_with_only_required_data)

    data = response.json()

    assert response.status_code == 200
    assert data["code"] == "A1"
    assert data["capacity"] == 3
    assert data["quantity"] == 0
    assert data["product_id"] is None
    assert data["id"] is not None

    example_product = _add_product_to_db(session, "Kinder Bueno", 290)

    slot_with_associated_product = {"code": "A2", "capacity": 3, "product_id": example_product.id}
    response = client.post("/slots", json=slot_with_associated_product)

    data = response.json()

    assert response.status_code == 200
    assert data["code"] == "A2"
    assert data["capacity"] == 3
    assert data["quantity"] == 0
    assert data["product_id"] == example_product.id
    assert data["id"] is not None

    slot_with_associated_product_and_quantity = {"code": "A3", "capacity": 3, "product_id": example_product.id, "quantity": 2}
    response = client.post("/slots", json=slot_with_associated_product_and_quantity)

    data = response.json()

    assert response.status_code == 200
    assert data["code"] == "A3"
    assert data["capacity"] == 3
    assert data["quantity"] == 2
    assert data["product_id"] == example_product.id
    assert data["id"] is not None


def test_get_slot(session: Session, client: TestClient):

    slot = _add_slot_to_db(session, "A1", 3)

    response = client.get(f"/slots/{slot.id}")
    
    data = response.json()

    assert response.status_code == 200
    assert data["code"] == slot.code
    assert data["capacity"] == slot.capacity
    assert data["quantity"] == slot.quantity
    assert data["product_id"] == slot.product_id
    assert data["id"] == slot.id


# def test_patch_product(session: Session, client: TestClient):

#     product = _add_product_to_db(session, "Kinder Bueno", 290)

#     new_name = "Doritos"
#     response = client.patch(f"/products/{product.id}", json={"name": new_name})

#     data = response.json()
#     assert response.status_code == 200
#     assert data["name"] == new_name

#     new_price = 250
#     response = client.patch(f"/products/{product.id}", json={"price": new_price})

#     data = response.json()
#     assert response.status_code == 200
#     assert data["price"] == new_price

#     new_data = {"name": "Bits", "price": 50}
#     response = client.patch(f"/products/{product.id}", json=new_data)

#     data = response.json()
#     assert response.status_code == 200
#     assert data["name"] == new_data["name"]
#     assert data["price"] == new_data["price"]


# def test_delete_product(session: Session, client: TestClient):

#     product = _add_product_to_db(session, "Kinder Bueno", 290)

#     response = client.delete(f"/products/{product.id}")
#     product_in_db = session.get(Product, product.id)

#     assert response.status_code == 204
#     assert product_in_db is None
 

# def test_get_all_products(session: Session, client: TestClient):

#     products_raw = [
#         {"name": "Kinder Bueno", "price": 290},
#         {"name": "Twix", "price": 180},
#         {"name": "Puleva", "price": 150}
#     ]

#     products = [_add_product_to_db(session, **product) for product in products_raw]

#     response = client.get("/products")

#     data = response.json()

#     assert response.status_code == 200
#     for i, product in enumerate(products):
#         assert data[i]["name"] == product.name
#         assert data[i]["price"] == product.price
#         assert data[i]["id"] == product.id


# def test_delete_non_existing_product(client: TestClient):

#     response = client.delete("/products/1")

#     assert response.status_code == 404


# def test_get_non_existing_product(client: TestClient):

#     response = client.get("/products/1")

#     assert response.status_code == 404


# def test_create_invalid_product(client):

#     product_with_invalid_name = {"name": "", "price": 250}
#     response = client.post("/products", json=product_with_invalid_name)
#     assert response.status_code == 422

#     product_with_invalid_price = {"name": "Kinder Bueno", "price": 0}
#     response = client.post("/products", json=product_with_invalid_price)
#     assert response.status_code == 422

#     product_with_missing_value = {"name": "Kinder Bueno"}
#     response = client.post("/products", json=product_with_missing_value)
#     assert response.status_code == 422
