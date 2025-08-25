from typing import Optional
from pydantic import BaseModel


class CustomerModel(BaseModel):
    customerId: str
    name: str
    phone: str
    address: str
    isMember: bool = False

class CustomerUpdateModel(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    isMember: Optional[bool] = None