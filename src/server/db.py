from typing import Dict, List, Optional
from .models import OrderOutput

class OrderRepository:
    """
    Repository class for managing orders in memory
    """
    def __init__(self):
        """Initialize an empty order database"""
        self._orders: Dict[str, OrderOutput] = {}

    def add(self, order: OrderOutput) -> None:
        """
        Add a new order to the database
        
        Args:
            order (OrderOutput): Order to be stored
        """
        self._orders[order.id] = order

    def get(self, order_id: str) -> Optional[OrderOutput]:
        """
        Retrieve an order by its ID
        
        Args:
            order_id (str): Unique identifier of the order
            
        Returns:
            Optional[OrderOutput]: Order if found, None otherwise
        """
        return self._orders.get(order_id)

    def get_all(self) -> List[OrderOutput]:
        """
        Retrieve all orders
        
        Returns:
            List[OrderOutput]: List of all orders
        """
        return list(self._orders.values())

    def update(self, order: OrderOutput) -> None:
        """
        Update an existing order
        
        Args:
            order (OrderOutput): Order with updated information
        """
        self._orders[order.id] = order

    def exists(self, order_id: str) -> bool:
        """
        Check if an order exists
        
        Args:
            order_id (str): Order ID to check
            
        Returns:
            bool: True if order exists, False otherwise
        """
        return order_id in self._orders
