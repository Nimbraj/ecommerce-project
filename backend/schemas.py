from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============== USER SCHEMAS ==============

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    address: Optional[str] = None
    mobile: Optional[str] = Field(None, pattern=r"^\d{10}$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    role: str
    is_banned: int
    is_admin: int
    two_factor_enabled: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserAdminCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    address: Optional[str] = None
    mobile: Optional[str] = Field(None, pattern=r"^\d{10}$")
    role: str = "customer"


class UserAdminUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    mobile: Optional[str] = None
    role: Optional[str] = None
    is_banned: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# ============== PRODUCT SCHEMAS ==============

class ProductBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    sku: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    image_url: Optional[str] = None
    status: Optional[str] = "active"
    is_featured: Optional[int] = 0
    stock_quantity: Optional[int] = 100
    low_stock_threshold: Optional[int] = 10
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    sku: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
    is_featured: Optional[int] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== CART SCHEMAS ==============

class CartBase(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartCreate(CartBase):
    pass


class CartResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: datetime
    product: ProductResponse

    class Config:
        from_attributes = True


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


# ============== REVIEW SCHEMAS ==============

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    product_id: int


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============== WISHLIST SCHEMAS ==============

class WishlistResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: ProductResponse

    class Config:
        from_attributes = True


# ============== ORDER SCHEMAS ==============

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)
    unit_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemBase]
    guest_email: Optional[EmailStr] = None
    guest_name: Optional[str] = None
    guest_mobile: Optional[str] = None
    guest_address: Optional[str] = None
    payment_method: Optional[str] = "card"
    coupon_code: Optional[str] = None


class DraftOrderCreate(BaseModel):
    items: List[OrderItemBase]
    user_id: Optional[int] = None
    guest_email: Optional[EmailStr] = None
    guest_name: Optional[str] = None
    guest_mobile: Optional[str] = None
    guest_address: Optional[str] = None
    payment_method: Optional[str] = "card"
    coupon_code: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    guest_email: Optional[str] = None
    guest_name: Optional[str] = None
    guest_mobile: Optional[str] = None
    guest_address: Optional[str] = None
    status: str
    payment_method: Optional[str] = None
    subtotal: float
    tax: float
    discount: float
    total: float
    coupon_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str


class OrderListResponse(BaseModel):
    id: int
    status: str
    total: float
    created_at: datetime
    item_count: int

    class Config:
        from_attributes = True


# ============== COUPON SCHEMAS ==============

class CouponBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    coupon_type: str = "percentage"
    value: float = Field(..., gt=0)
    min_order_value: Optional[float] = 0
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = 1
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class CouponCreate(CouponBase):
    pass


class CouponResponse(CouponBase):
    id: int
    usage_count: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class CouponValidate(BaseModel):
    code: str
    order_total: float


class CouponApplyResponse(BaseModel):
    valid: bool
    discount: float
    message: str


# ============== CATEGORY SCHEMAS ==============

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== TAX RULE SCHEMAS ==============

class TaxRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    rate: float = Field(..., ge=0)
    country: Optional[str] = None
    region: Optional[str] = None
    is_active: Optional[int] = 1


class TaxRuleCreate(TaxRuleBase):
    pass


class TaxRuleUpdate(BaseModel):
    name: Optional[str] = None
    rate: Optional[float] = Field(None, ge=0)
    country: Optional[str] = None
    region: Optional[str] = None
    is_active: Optional[int] = None


class TaxRuleResponse(TaxRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== AUDIT LOG SCHEMAS ==============

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== INVENTORY / ANALYTICS SCHEMAS ==============

class InventoryUpdate(BaseModel):
    stock_quantity: int = Field(..., ge=0)
    low_stock_threshold: Optional[int] = None


class LowStockResponse(BaseModel):
    id: int
    title: str
    stock_quantity: int
    low_stock_threshold: int
    category: str

    class Config:
        from_attributes = True


class SalesSummary(BaseModel):
    total_orders: int
    total_revenue: float
    total_customers: int
    average_order_value: float


class TopProduct(BaseModel):
    product_id: int
    title: str
    total_sold: int
    total_revenue: float


class AdminAnalytics(BaseModel):
    sales_summary: SalesSummary
    top_products: List[TopProduct]
    recent_orders: List[OrderListResponse]
    low_stock_items: List[LowStockResponse]


# ============== MESSAGE SCHEMAS ==============

class Message(BaseModel):
    message: str

