from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from api.models import Product
from api.schemas import ProductCreate


def _add_product_to_db(session, name: str, price: str):
    product = Product(**ProductCreate(name=name, price=price).model_dump())
    session.add(product)
    session.commit()
    return product


def test_create_valid_product(client: TestClient):

    product = {"name": "Kinder Bueno", "price": 290}
    response = client.post("/products", json=product)

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Kinder Bueno"
    assert data["price"] == 290
    assert data["id"] is not None


def test_get_product(session: Session, client: TestClient):

    product = _add_product_to_db(session, "Kinder Bueno", 290)

    response = client.get(f"/products/{product.id}")
    
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == product.name
    assert data["price"] == product.price
    assert data["id"] == product.id


def test_patch_product(session: Session, client: TestClient):

    product = _add_product_to_db(session, "Kinder Bueno", 290)

    new_name = "Doritos"
    response = client.patch(f"/products/{product.id}", json={"name": new_name})

    data = response.json()
    assert response.status_code == 200
    assert data["name"] == new_name

    new_price = 250
    response = client.patch(f"/products/{product.id}", json={"price": new_price})

    data = response.json()
    assert response.status_code == 200
    assert data["price"] == new_price

    new_data = {"name": "Bits", "price": 50}
    response = client.patch(f"/products/{product.id}", json=new_data)

    data = response.json()
    assert response.status_code == 200
    assert data["name"] == new_data["name"]
    assert data["price"] == new_data["price"]


def test_delete_product(session: Session, client: TestClient):

    product = _add_product_to_db(session, "Kinder Bueno", 290)

    response = client.delete(f"/products/{product.id}")
    product_in_db = session.get(Product, product.id)

    assert response.status_code == 204
    assert product_in_db is None
 

def test_get_all_products(session: Session, client: TestClient):

    products_raw = [
        {"name": "Kinder Bueno", "price": 290},
        {"name": "Twix", "price": 180},
        {"name": "Puleva", "price": 150}
    ]

    products = [_add_product_to_db(session, **product) for product in products_raw]

    response = client.get("/products")

    data = response.json()

    assert response.status_code == 200
    for i, product in enumerate(products):
        assert data[i]["name"] == product.name
        assert data[i]["price"] == product.price
        assert data[i]["id"] == product.id


def test_delete_non_existing_product(client: TestClient):

    response = client.delete("/products/1")

    assert response.status_code == 404


def test_get_non_existing_product(client: TestClient):

    response = client.get("/products/1")

    assert response.status_code == 404


def test_create_invalid_product(client):

    product_with_invalid_name = {"name": "", "price": 250}
    response = client.post("/products", json=product_with_invalid_name)
    assert response.status_code == 422

    product_with_invalid_price = {"name": "Kinder Bueno", "price": 0}
    response = client.post("/products", json=product_with_invalid_price)
    assert response.status_code == 422

    product_with_missing_value = {"name": "Kinder Bueno"}
    response = client.post("/products", json=product_with_missing_value)
    assert response.status_code == 422
