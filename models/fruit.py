from pydantic import BaseModel
from typing import Optional


class FruitModel(BaseModel):
    barCode: str
    name: str
    category: str
    pricePerKg: float
    stockKg: int
    country: str
    supplierId: str
    isOrganic: bool = False

class FruitUpdateModel(BaseModel):
    barCode: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    pricePerKg: Optional[float] = None
    stockKg: Optional[int] = None
    country: Optional[str] = None
    supplierId: Optional[str] = None
    isOrganic: Optional[bool] = None