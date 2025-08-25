from typing import List, Optional
from pydantic import BaseModel


class SupplierModel(BaseModel):
    name: str
    phone: str
    location: str
    fruitsSupplied: List[str]
    active: bool = True

class SupplierUpdateModel(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    fruitsSupplied: Optional[List[str]] = None
    active: Optional[bool] = None