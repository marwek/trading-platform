import asyncio
import pytest

@pytest.mark.asyncio
async def test_websocket_connection(client):
    """Test WebSocket connection can be established"""
    with client.websocket_connect("/ws") as websocket:
        # Send message
        websocket.send_text("get_orders")
        
        # Get response
        data = websocket.receive_json()
        
        # Verify response format
        assert "type" in data
        assert data["type"] == "orders_update"
        assert "data" in data
        assert isinstance(data["data"], list)