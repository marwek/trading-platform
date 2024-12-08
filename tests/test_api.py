import asyncio
import pytest


@pytest.mark.asyncio
async def test_create_order(client):
    response = client.post("/orders", json={"stocks": "ZXCV", "quantity": 10})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "PENDING"

@pytest.mark.asyncio
async def test_get_orders(client):
    # Ensure the order list is initially empty
    response = client.get("/orders")
    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)

    # Add a new order and check it's reflected in the list
    client.post("/orders", json={"stocks": "ASDF", "quantity": 10})
    response = client.get("/orders")
    orders = response.json()
    assert len(orders) == 1

@pytest.mark.asyncio
async def test_get_order_by_id(client):
    # Create a new order
    create_response = client.post("/orders", json={"stocks": "QWER", "quantity": 5})
    order_id = create_response.json()["id"]

    # Fetch the order by ID
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["stocks"] == "QWER"
    assert data["quantity"] == 5

@pytest.mark.asyncio
async def test_cancel_pending_order(client):
    # Create a new order
    create_response = client.post("/orders", json={"stocks": "MNBV", "quantity": 2})
    order_id = create_response.json()["id"]

    # Cancel the order
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 200

    # Verify the order's status is CANCELLED
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"

@pytest.mark.asyncio
async def test_execute_order(client):
    # Create a new order
    create_response = client.post("/orders", json={"stocks": "LKJH", "quantity": 20})
    order_id = create_response.json()["id"]

    # Allow the order to auto-execute and fetch the status
    await asyncio.sleep(2)
    response = client.post(f"/orders/{order_id}/execute")
    assert response.status_code == 200
    assert response.json()["status"] == "EXECUTED"
