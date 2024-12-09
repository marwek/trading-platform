import random
import uuid
import logging
from datetime import datetime
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from typing import List

from .models import OrderInput, OrderOutput, Error, HealthCheck, OrderStatus
from .db import OrderRepository

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="Forex Trading Platform API")

# Initialize database
order_repository = OrderRepository()

# Active WebSocket connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time order updates
    
    Args:
        websocket (WebSocket): WebSocket connection instance
    """
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            if data == "ping":
                await websocket.send_text("pong")
                continue
            
            if data == "get_orders":
                # Send current orders status
                current_orders = order_repository.get_all()
                message = {
                    "type": "orders_update",
                    "data": [
                        {
                            "order_id": order.id,
                            "status": order.status,
                            "stocks": order.stocks,
                            "quantity": order.quantity,
                        } for order in current_orders
                    ]
                }
                logger.info(f"Sending message: {message}")
                await websocket.send_json(message)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if websocket in active_connections:
            active_connections.remove(websocket)

async def notify_status_change(order: OrderOutput):
    """
    Notify all connected clients about order status changes
    
    Args:
        order (OrderOutput): The order that was updated
    """
    if active_connections:
        message = {
            "type": "status_change",
            "data": {
                "order_id": order.id,
                "status": order.status,
                "stocks": order.stocks,
                "quantity": order.quantity,
                "timestamp": datetime.now().isoformat()
            }
        }
        print(f"Broadcasting status change: {message}")  # Debug log
        
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                print(f"Error sending message: {str(e)}")  # Debug log
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            if connection in active_connections:
                active_connections.remove(connection)

async def simulate_delay():
    """
    Simulates network or processing delay
    
    Adds a random delay between 0.1 and 1 second to make the API behave more realistically
    """
    delay = random.uniform(0.1, 1.0)
    await asyncio.sleep(delay)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Check the health status of the service
    
    Returns:
        HealthCheck: Object containing service status and current timestamp
    """
    logger.info("Health check endpoint called")
    return HealthCheck(
        status="ok",
        date=datetime.now().isoformat()
    )

@app.get("/orders", response_model=List[OrderOutput])
async def get_orders():
    """
    Retrieve all orders in the system
    
    Returns:
        List[OrderOutput]: List of all orders with their current status
    """
    logger.info("Get orders endpoint called")
    await simulate_delay()
    return order_repository.get_all()

@app.post("/orders", response_model=OrderOutput, status_code=201)
async def place_order(order: OrderInput):
    """
    Place a new order in the system
    
    Args:
        order (OrderInput): Order details including stock symbol and quantity
    
    Returns:
        OrderOutput: Created order with assigned ID and PENDING status
    """
    logger.info(f"Place order endpoint called with order: stocks='{order.stocks}' quantity={order.quantity}")
    await simulate_delay()
    
    order_id = str(uuid.uuid4())
    order_output = OrderOutput(
        id=order_id,
        stocks=order.stocks,
        quantity=order.quantity,
        status=OrderStatus.PENDING
    )
    order_repository.add(order_output)
    
    await notify_status_change(order_output)
    logger.info(f"Order placed: {order_output}")
    return order_output

@app.post("/orders/{order_id}/execute", response_model=OrderOutput)
async def execute_order(order_id: str):
    """
    Execute a pending order
    
    Args:
        order_id (str): Unique identifier of the order to execute
    
    Returns:
        OrderOutput: Updated order with EXECUTED status
    
    Raises:
        HTTPException: 404 if order not found or 400 if order cannot be executed
    """
    await simulate_delay()
    
    order = order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=Error(code=404, message="Order not found").model_dump()
        )
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=Error(
                code=400, 
                message=f"Cannot execute order in {order.status} status. Only PENDING orders can be executed."
            ).model_dump()
        )
    
    order.status = OrderStatus.EXECUTED
    order_repository.update(order)
    await notify_status_change(order)
    return order

@app.get("/orders/{order_id}", response_model=OrderOutput)
async def get_order(order_id: str):
    """
    Retrieve a specific order by ID
    
    Args:
        order_id (str): Unique identifier of the order to retrieve
    
    Returns:
        OrderOutput: Order details if found
    
    Raises:
        HTTPException: 404 if order not found
    """
    await simulate_delay()
    
    order = order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=Error(code=404, message="Order not found").model_dump()
        )
    return order

@app.delete("/orders/{order_id}", response_model=OrderOutput)
async def cancel_order(order_id: str):
    """
    Cancel a pending order
    
    Args:
        order_id (str): Unique identifier of the order to cancel
    
    Returns:
        OrderOutput: Cancelled order with updated status
    
    Raises:
        HTTPException: 404 if order not found or 400 if order cannot be cancelled
    """
    await simulate_delay()
    
    order = order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=Error(code=404, message="Order not found").model_dump()
        )
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=Error(
                code=400, 
                message=f"Cannot cancel order in {order.status} status. Only PENDING orders can be cancelled."
            ).model_dump()
        )
    
    order.status = OrderStatus.CANCELLED
    order_repository.update(order)
    await notify_status_change(order)
    return order
