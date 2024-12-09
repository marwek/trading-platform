from enum import Enum
from typing import Optional

from pydantic import BaseModel


class OrderStatus(str, Enum):
    """Enumeration for possible order statuses"""

    EXECUTED = "EXECUTED"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"


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
        order_date: Timestamp when the order was placed
        executed_date: Timestamp when the order was executed
    """

    id: str
    stocks: str
    quantity: float
    status: OrderStatus
    order_date: Optional[float]
    executed_date: Optional[float] = None


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
    date: Optional[float]
