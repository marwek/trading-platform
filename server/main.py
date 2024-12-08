import os
import random
import uuid
from datetime import datetime
from enum import Enum
from typing import List
from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OrderStatus(str, Enum):
    """Enumeration for possible order statuses"""
    EXECUTED = "EXECUTED"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"

app = FastAPI(title="Forex Trading Platform API")

# In-memory database
orders_db = {}

class OrderInput(BaseModel):
    """
    Input model for creating orders
    
    Attributes:
        stocks: Symbol of the stock being traded
        quantity: Number of shares to trade
    """
    stocks: str
    quantity: float

class OrderOutput(BaseModel):
    """
    Output model for order information
    
    Attributes:
        id: Unique identifier for the order
        stocks: Symbol of the stock being traded
        quantity: Number of shares to trade
        status: Current status of the order
    """
    id: str
    stocks: str
    quantity: float
    status: OrderStatus

class Error(BaseModel):
    """
    Error response model
    
    Attributes:
        code: HTTP status code
        message: Descriptive error message
    """
    code: int
    message: str

class HealthCheck(BaseModel):
    """
    Health check response model
    
    Attributes:
        status: Current status of the service
        date: Timestamp of the health check
    """
    status: str
    date: str

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
    await simulate_delay()
    return list(orders_db.values())

@app.post("/orders", response_model=OrderOutput, status_code=201)
async def place_order(order: OrderInput):
    """
    Place a new order in the system
    
    Args:
        order (OrderInput): Order details including stock symbol and quantity
    
    Returns:
        OrderOutput: Created order with assigned ID and PENDING status
    """
    await simulate_delay()
    
    order_id = str(uuid.uuid4())
    order_output = OrderOutput(
        id=order_id,
        stocks=order.stocks,
        quantity=order.quantity,
        status=OrderStatus.PENDING
    )
    orders_db[order_id] = order_output
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
    
    if order_id not in orders_db:
        raise HTTPException(
            status_code=404,
            detail=Error(code=404, message="Order not found").model_dump()
        )
    
    current_status = orders_db[order_id].status
    
    if current_status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=Error(
                code=400, 
                message=f"Cannot execute order in {current_status} status. Only PENDING orders can be executed."
            ).model_dump()
        )
    
    orders_db[order_id].status = OrderStatus.EXECUTED
    return orders_db[order_id]

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
    
    if order_id not in orders_db:
        raise HTTPException(
            status_code=404,
            detail=Error(code=404, message="Order not found").model_dump()
        )
    return orders_db[order_id]

@app.delete("/orders/{order_id}", status_code=204)
async def cancel_order(order_id: str):
    """
    Cancel a pending order
    
    Args:
        order_id (str): Unique identifier of the order to cancel
    
    Returns:
        None
    
    Raises:
        HTTPException: 404 if order not found or 400 if order cannot be cancelled
    """
    await simulate_delay()
    
    if order_id not in orders_db:
        raise HTTPException(
            status_code=404,
            detail=Error(code=404, message="Order not found").model_dump()
        )
    
    current_status = orders_db[order_id].status
    
    if current_status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=Error(
                code=400, 
                message=f"Cannot cancel order in {current_status} status. Only PENDING orders can be cancelled."
            ).model_dump()
        )
    
    orders_db[order_id].status = OrderStatus.CANCELLED
    return None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time order updates
    
    Args:
        websocket (WebSocket): WebSocket connection instance
    
    Note:
        Currently implements a simple echo service. In a production environment,
        this would broadcast real-time order status updates to connected clients.
    """
    await websocket.accept()
    try:
        while True:
            # keep the connection alive
            await websocket.receive_text()
            await websocket.send_json({"message": "Order status update"})
    except Exception:
        await websocket.close()