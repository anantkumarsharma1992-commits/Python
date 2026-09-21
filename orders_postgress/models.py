"""
models.py

Pydantic models - the "name-tag forms" that every request must fill out
correctly before FastAPI lets it reach our actual database code.
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None
    price: float = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    category: str = Field(min_length=2, max_length=50)


class InventoryUpdate(BaseModel):
    stock_quantity: int = Field(ge=0)


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate] = Field(min_length=1)
