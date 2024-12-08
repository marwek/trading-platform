from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import random
import uuid

app = FastAPI()

class Order(BaseModel):
    id: str
    status: str

orders: Dict[str, Order] = {}
clients: List[WebSocket] = []

@app.get("/orders")
async def get_orders():
    await asyncio.sleep(random.uniform(0.1, 1))
    return list(orders.values())

@app.post("/orders")
async def create_order():
    await asyncio.sleep(random.uniform(0.1, 1))
    order_id = str(uuid.uuid4())
    order = Order(id=order_id, status="PENDING")
    orders[order_id] = order
    asyncio.create_task(update_order_status(order_id))
    return {"orderId": order_id}

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    await asyncio.sleep(random.uniform(0.1, 1))
    order = orders.get(order_id)
    if order:
        return order
    return JSONResponse(status_code=404, content={"message": "Order not found"})

@app.delete("/orders/{order_id}")
async def delete_order(order_id: str):
    await asyncio.sleep(random.uniform(0.1, 1))
    order = orders.get(order_id)
    if order and order.status == "PENDING":
        order.status = "CANCELLED"
        await notify_clients(order)
        return {"message": "Order cancelled"}
    return JSONResponse(status_code=404, content={"message": "Order not found or cannot be cancelled"})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

async def update_order_status(order_id: str):
    await asyncio.sleep(random.uniform(0.1, 1))
    order = orders.get(order_id)
    if order and order.status == "PENDING":
        order.status = "EXECUTED"
        await notify_clients(order)

async def notify_clients(order: Order):
    for client in clients:
        await client.send_json({"orderId": order.id, "status": order.status})