import random

import pytest


@pytest.mark.websocket
async def test_websocket_basic_connection(client):
    """Test basic WebSocket connection and disconnection"""
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("get_orders")
        data = websocket.receive_json()
        assert "type" in data
        assert data["type"] == "orders_update"


@pytest.mark.websocket
async def test_order_status_events(client):
    """Test real-time order status events through WebSocket"""
    with client.websocket_connect("/ws") as websocket:
        # Create a new order via REST API
        order_data = {"stocks": "AAAA", "quantity": random.random() * 100}
        order_response = client.post("/orders", json=order_data)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]

        # Receive and verify PENDING status
        data = websocket.receive_json()
        assert data["type"] == "status_change"
        assert data["data"]["order_id"] == order_id
        assert data["data"]["status"] == "PENDING"

        # Execute the order
        execute_response = client.post(f"/orders/{order_id}/execute")
        assert execute_response.status_code == 200

        # # Receive and verify EXECUTED status
        data = websocket.receive_json()
        assert data["type"] == "status_change"
        assert data["data"]["order_id"] == order_id
        assert data["data"]["status"] == "EXECUTED"


@pytest.mark.websocket
async def test_order_status_sequence(client):
    """Test the correct sequence of order status events"""
    status_sequence = []

    with client.websocket_connect("/ws") as websocket:
        # Create order
        order_data = {"stocks": "EEEE", "quantity": 100.0}
        order_response = client.post("/orders", json=order_data)
        order_id = order_response.json()["id"]

        # Collect first status (should be PENDING)
        data = websocket.receive_json()
        status_sequence.append(data["data"]["status"])

        # Execute order
        client.post(f"/orders/{order_id}/execute")

        # Collect second status (should be EXECUTED)
        data = websocket.receive_json()
        status_sequence.append(data["data"]["status"])

        # Verify sequence
        assert status_sequence == ["PENDING", "EXECUTED"]


async def test_no_messages_after_cancel(client):
    """Test that no status updates are received after order cancellation"""
    with client.websocket_connect("/ws") as websocket:
        # Create order
        order_data = {"stocks": "XXXX", "quantity": 100.0}
        order_response = client.post("/orders", json=order_data)
        order_id = order_response.json()["id"]

        # Get PENDING status
        data = websocket.receive_json()
        assert data["data"]["status"] == "PENDING"

        # Cancel order
        cancel_response = client.delete(f"/orders/{order_id}")
        assert cancel_response.status_code == 200

        # Get CANCELLED status
        data = websocket.receive_json()
        assert data["data"]["status"] == "CANCELLED"

        # Try to execute cancelled order
        execute_response = client.post(f"/orders/{order_id}/execute")
        assert execute_response.status_code == 400

        # Verify no more messages are received
        with pytest.raises(Exception):
            websocket.receive_json(timeout=1.0)
