from typing import List, Optional
from pydantic import BaseModel


class OrderItemModel(BaseModel):
    fruitId: str
    quantityKg: float

class OrderModel(BaseModel):
    customerId: str
    items: List[OrderItemModel]
    status: str = "Pending"

class OrderUpdateModel(BaseModel):
    status: Optional[str] = None