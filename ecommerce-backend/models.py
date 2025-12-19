from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    user_type: int

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    phone: str
    email: str
    user_type: int = 0

class ProductSearch(BaseModel):
    keyword: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    page: int = 1
    page_size: int = 20

class CartItem(BaseModel):
    product_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    address_id: int
    cart_ids: List[int]
    shipping_fee: float = 0.0  # 添加这个字段
    remark: Optional[str] = None
