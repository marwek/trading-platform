import pytest


@pytest.mark.asyncio
async def test_create_order_invalid_data(client):
    # Missing required fields
    response = client.post("/orders", json={})
    assert response.status_code == 422

    # Invalid data types
    response = client.post("/orders", json={"stocks": 123, "quantity": "ten"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_non_existent_order(client):
    # Using an invalid or non-existent order ID
    response = client.get("/orders/non_existent_id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cancel_non_existent_order(client):
    # Using an invalid or non-existent order ID
    response = client.delete("/orders/non_existent_id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cancel_non_cancellable_order(client):
    # Create a new order
    create_response = client.post("/orders", json={"stocks": "MNBV", "quantity": 2})
    order_id = create_response.json()["id"]

    # Execute the order
    response = client.post(f"/orders/{order_id}/execute")
    assert response.status_code == 200

    # Try to cancel the executed order
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_execute_non_existent_order(client):
    # Using an invalid or non-existent order ID
    response = client.post("/orders/non_existent_id/execute")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_execute_non_executable_order(client):
    # Create a new order
    create_response = client.post("/orders", json={"stocks": "MNBV", "quantity": 2})
    order_id = create_response.json()["id"]

    # Cancel the order
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 200

    # Try to execute the canceled order
    response = client.post(f"/orders/{order_id}/execute")
    assert response.status_code == 400
