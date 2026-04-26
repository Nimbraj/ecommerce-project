import os
from datetime import datetime, timedelta
from typing import List, Optional, Union
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from passlib.context import CryptContext
from jose import JWTError, jwt
import pyotp
import re

# ============== DATABASE SETUP ==============
SQLALCHEMY_DATABASE_URL = "sqlite:///./shopswift.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============== SECURITY SETUP ==============
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# ============== MODELS ==============
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    role = Column(String, default="user")
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cart_items = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    wishlist_items = relationship("Wishlist", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String)
    image_url = Column(String)
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=5)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    cart_items = relationship("Cart", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    wishlist_items = relationship("Wishlist", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    total = Column(Float, default=0.0)
    shipping_address = Column(Text)
    coupon_code = Column(String, nullable=True)
    discount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")

class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_percent = Column(Float)
    min_order_amount = Column(Float, default=0.0)
    max_discount = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    usage_limit = Column(Integer, default=100)
    used_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TaxRule(Base):
    __tablename__ = "tax_rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    region = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")

# Create tables
Base.metadata.create_all(bind=engine)

# ============== SCHEMAS ==============
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    admin_key: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_admin: bool
    role: str
    is_banned: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    stock_quantity: int = 0
    low_stock_threshold: int = 5

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    status: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    category: str
    image_url: Optional[str]
    stock_quantity: int
    low_stock_threshold: int
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class CartCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductResponse
    
    class Config:
        orm_mode = True

class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    comment: str

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: str
    created_at: datetime
    user_name: Optional[str]
    
    class Config:
        orm_mode = True

class WishlistResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: ProductResponse
    
    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    shipping_address: str
    coupon_code: Optional[str] = None

class OrderListResponse(BaseModel):
    id: int
    status: str
    total: float
    created_at: datetime
    item_count: int

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total: float
    shipping_address: str
    coupon_code: Optional[str]
    discount: float
    created_at: datetime
    items: list
    
    class Config:
        orm_mode = True

class OrderStatusUpdate(BaseModel):
    status: str

class DraftOrderCreate(BaseModel):
    user_id: int
    items: List[dict]
    shipping_address: str
    coupon_code: Optional[str] = None

class CouponCreate(BaseModel):
    code: str
    discount_percent: float
    min_order_amount: float = 0.0
    max_discount: Optional[float] = None
    valid_from: datetime
    valid_until: datetime
    usage_limit: int = 100

class CouponValidate(BaseModel):
    code: str
    order_total: float

class CouponApplyResponse(BaseModel):
    valid: bool
    discount_amount: float
    final_total: float
    message: str

class CouponResponse(BaseModel):
    id: int
    code: str
    discount_percent: float
    min_order_amount: float
    max_discount: Optional[float]
    is_active: bool
    valid_from: datetime
    valid_until: datetime
    usage_limit: int
    used_count: int
    
    class Config:
        orm_mode = True

class InventoryUpdate(BaseModel):
    stock_quantity: int
    low_stock_threshold: Optional[int] = None

class LowStockResponse(BaseModel):
    id: int
    title: str
    stock_quantity: int
    low_stock_threshold: int
    category: str

class UserAdminCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = "user"

class UserAdminUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_admin: Optional[bool] = None

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class TaxRuleCreate(BaseModel):
    name: str
    rate: float
    region: Optional[str] = None

class TaxRuleUpdate(BaseModel):
    name: Optional[str] = None
    rate: Optional[float] = None
    region: Optional[str] = None
    is_active: Optional[bool] = None

class TaxRuleResponse(BaseModel):
    id: int
    name: str
    rate: float
    region: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str]
    action: str
    entity_type: str
    entity_id: int
    details: str
    created_at: datetime

class AdminAnalytics(BaseModel):
    sales_summary: dict
    top_products: list
    recent_orders: list
    low_stock_items: list

class Message(BaseModel):
    message: str

# ============== DATABASE DEPENDENCY ==============
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============== AUTH FUNCTIONS ==============
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(secret, email):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="ShopSwift")

def verify_totp(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

def check_password_strength(password):
    issues = []
    if len(password) < 8:
        issues.append("at least 8 characters")
    if not re.search(r'[A-Z]', password):
        issues.append("one uppercase letter")
    if not re.search(r'[a-z]', password):
        issues.append("one lowercase letter")
    if not re.search(r'\d', password):
        issues.append("one number")
    
    if issues:
        return {"valid": False, "message": f"Password must contain {', '.join(issues)}"}
    return {"valid": True, "message": "Password is strong"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.is_banned:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in ["admin"] and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_manager_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "manager"] and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# ============== CRUD FUNCTIONS ==============
def create_user(db: Session, user: UserCreate, is_admin: int = 0):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        is_admin=bool(is_admin),
        role="admin" if is_admin else "user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None):
    query = db.query(User)
    if search:
        query = query.filter(
            (User.name.contains(search)) | (User.email.contains(search))
        )
    return query.offset(skip).limit(limit).all()

def create_admin_user(db: Session, user: UserAdminCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        role=user.role,
        is_admin=(user.role == "admin")
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_admin(db: Session, user_id: int, update: UserAdminUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    if update.name is not None:
        db_user.name = update.name
    if update.role is not None:
        db_user.role = update.role
        db_user.is_admin = (update.role == "admin")
    if update.is_admin is not None:
        db_user.is_admin = update.is_admin
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

def ban_user(db: Session, user_id: int, banned: bool = True):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    db_user.is_banned = banned
    db.commit()
    db.refresh(db_user)
    return db_user

def log_audit_action(db: Session, user_id: int, action: str, entity_type: str, entity_id: int, details: str):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.add(audit)
    db.commit()

def get_products(db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None, status: Optional[str] = None):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Product.status == status)
    else:
        query = query.filter(Product.status == "active")
    return query.offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product: ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    db.delete(db_product)
    db.commit()
    return db_product

def get_cart_items(db: Session, user_id: int):
    return db.query(Cart).filter(Cart.user_id == user_id).all()

def add_to_cart(db: Session, user_id: int, cart: CartCreate):
    existing = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.product_id == cart.product_id
    ).first()
    
    if existing:
        existing.quantity += cart.quantity
        db.commit()
        db.refresh(existing)
        return existing
    
    db_cart = Cart(user_id=user_id, product_id=cart.product_id, quantity=cart.quantity)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def update_cart_item(db: Session, cart_id: int, user_id: int, quantity: int):
    cart_item = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id).first()
    if not cart_item:
        return None
    if quantity <= 0:
        db.delete(cart_item)
        db.commit()
        return None
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

def remove_from_cart(db: Session, cart_id: int, user_id: int):
    cart_item = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id).first()
    if not cart_item:
        return False
    db.delete(cart_item)
    db.commit()
    return True

def clear_cart(db: Session, user_id: int):
    db.query(Cart).filter(Cart.user_id == user_id).delete()
    db.commit()

def get_reviews(db: Session, product_id: int):
    return db.query(Review).filter(Review.product_id == product_id).all()

def create_review(db: Session, user_id: int, review: ReviewCreate):
    db_review = Review(
        user_id=user_id,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_review(db: Session, review_id: int, user_id: int):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == user_id).first()
    if not review:
        return False
    db.delete(review)
    db.commit()
    return True

def get_wishlist(db: Session, user_id: int):
    return db.query(Wishlist).filter(Wishlist.user_id == user_id).all()

def add_to_wishlist(db: Session, user_id: int, product_id: int):
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).first()
    if existing:
        return existing
    wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return wishlist_item

def remove_from_wishlist(db: Session, wishlist_id: int, user_id: int):
    item = db.query(Wishlist).filter(Wishlist.id == wishlist_id, Wishlist.user_id == user_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True

def search_products(db: Session, query: str):
    return db.query(Product).filter(
        (Product.title.contains(query)) |
        (Product.description.contains(query)) |
        (Product.category.contains(query))
    ).filter(Product.status == "active").all()

def create_order(db: Session, user_id: int, order: OrderCreate):
    cart_items = get_cart_items(db, user_id)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    discount = 0
    
    if order.coupon_code:
        coupon_result = validate_coupon(db, order.coupon_code, total)
        if coupon_result["valid"]:
            discount = coupon_result["discount_amount"]
            coupon = db.query(Coupon).filter(Coupon.code == order.coupon_code).first()
            coupon.used_count += 1
        else:
            raise HTTPException(status_code=400, detail=coupon_result["message"])
    
    final_total = total - discount
    
    db_order = Order(
        user_id=user_id,
        total=final_total,
        shipping_address=order.shipping_address,
        coupon_code=order.coupon_code,
        discount=discount
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        product = cart_item.product
        product.stock_quantity -= cart_item.quantity
        db.add(order_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

def get_all_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

def update_order_status(db: Session, order_id: int, status_update: OrderStatusUpdate):
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    db_order.status = status_update.status
    db_order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_order)
    return db_order

def create_draft_order(db: Session, order: DraftOrderCreate):
    total = sum(item["price"] * item["quantity"] for item in order.items)
    discount = 0
    
    if order.coupon_code:
        coupon_result = validate_coupon(db, order.coupon_code, total)
        if coupon_result["valid"]:
            discount = coupon_result["discount_amount"]
    
    db_order = Order(
        user_id=order.user_id,
        total=total - discount,
        shipping_address=order.shipping_address,
        coupon_code=order.coupon_code,
        discount=discount,
        status="draft"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for item in order.items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"]
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def cancel_order(db: Session, order_id: int):
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    db_order.status = "cancelled"
    db_order.updated_at = datetime.utcnow()
    
    for item in db_order.items:
        product = item.product
        product.stock_quantity += item.quantity
    
    db.commit()
    db.refresh(db_order)
    return db_order

def refund_order(db: Session, order_id: int):
    db_order = get_order(db, order_id)
    if not db_order or db_order.status != "delivered":
        return None
    db_order.status = "refunded"
    db_order.updated_at = datetime.utcnow()
    
    for item in db_order.items:
        product = item.product
        product.stock_quantity += item.quantity
    
    db.commit()
    db.refresh(db_order)
    return db_order

def create_coupon(db: Session, coupon: CouponCreate):
    db_coupon = Coupon(**coupon.dict())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def get_all_coupons(db: Session):
    return db.query(Coupon).all()

def validate_coupon(db: Session, code: str, order_total: float):
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    
    if not coupon:
        return {"valid": False, "discount_amount": 0, "final_total": order_total, "message": "Invalid coupon code"}
    
    if not coupon.is_active:
        return {"valid": False, "discount_amount": 0, "final_total": order_total, "message": "Coupon is not active"}
    
    now = datetime.utcnow()
    if now < coupon.valid_from or now > coupon.valid_until:
        return {"valid": False, "discount_amount": 0, "final_total": order_total, "message": "Coupon has expired"}
    
    if coupon.used_count >= coupon.usage_limit:
        return {"valid": False, "discount_amount": 0, "final_total": order_total, "message": "Coupon usage limit reached"}
    
    if order_total < coupon.min_order_amount:
        return {"valid": False, "discount_amount": 0, "final_total": order_total, "message": f"Minimum order amount of ${coupon.min_order_amount} required"}
    
    discount = order_total * (coupon.discount_percent / 100)
    if coupon.max_discount and discount > coupon.max_discount:
        discount = coupon.max_discount
    
    final_total = order_total - discount
    return {"valid": True, "discount_amount": discount, "final_total": final_total, "message": "Coupon applied successfully"}

def delete_coupon(db: Session, coupon_id: int):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        return False
    db.delete(coupon)
    db.commit()
    return True

def update_inventory(db: Session, product_id: int, stock_quantity: int, low_stock_threshold: Optional[int] = None):
    product = get_product(db, product_id)
    if not product:
        return None
    product.stock_quantity = stock_quantity
    if low_stock_threshold is not None:
        product.low_stock_threshold = low_stock_threshold
    db.commit()
    db.refresh(product)
    return product

def get_low_stock_products(db: Session):
    return db.query(Product).filter(
        Product.stock_quantity <= Product.low_stock_threshold,
        Product.status == "active"
    ).all()

def get_sales_summary(db: Session):
    today = datetime.utcnow().date()
    start_of_today = datetime(today.year, today.month, today.day)
    
    total_sales = db.query(Order).filter(
        Order.status.in_(["delivered", "shipped", "processing"])
    ).count()
    
    today_sales = db.query(Order).filter(
        Order.created_at >= start_of_today,
        Order.status.in_(["delivered", "shipped", "processing"])
    ).count()
    
    revenue_query = db.query(Order).filter(
        Order.status.in_(["delivered", "shipped", "processing"])
    )
    total_revenue = sum(order.total for order in revenue_query.all())
    
    today_revenue = sum(order.total for order in revenue_query.filter(Order.created_at >= start_of_today).all())
    
    return {
        "total_orders": total_sales,
        "today_orders": today_sales,
        "total_revenue": total_revenue,
        "today_revenue": today_revenue
    }

def get_top_products(db: Session, limit: int = 5):
    orders = db.query(Order).filter(Order.status.in_(["delivered", "shipped"])).all()
    product_sales = {}
    
    for order in orders:
        for item in order.items:
            if item.product_id in product_sales:
                product_sales[item.product_id]["quantity"] += item.quantity
                product_sales[item.product_id]["revenue"] += item.quantity * item.price
            else:
                product_sales[item.product_id] = {
                    "product": item.product,
                    "quantity": item.quantity,
                    "revenue": item.quantity * item.price
                }
    
    sorted_products = sorted(product_sales.values(), key=lambda x: x["quantity"], reverse=True)
    top_products = []
    
    for sp in sorted_products[:limit]:
        top_products.append({
            "id": sp["product"].id,
            "title": sp["product"].title,
            "total_sold": sp["quantity"],
            "total_revenue": sp["revenue"]
        })
    
    return top_products

def get_recent_orders(db: Session, limit: int = 10):
    return db.query(Order).order_by(Order.created_at.desc()).limit(limit).all()

def create_category(db: Session, category: CategoryCreate):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session):
    return db.query(Category).all()

def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def update_category(db: Session, category_id: int, update: CategoryUpdate):
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    db.delete(db_category)
    db.commit()
    return True

def create_tax_rule(db: Session, tax: TaxRuleCreate):
    db_tax = TaxRule(**tax.dict())
    db.add(db_tax)
    db.commit()
    db.refresh(db_tax)
    return db_tax

def get_tax_rules(db: Session):
    return db.query(TaxRule).all()

def get_tax_rule(db: Session, tax_id: int):
    return db.query(TaxRule).filter(TaxRule.id == tax_id).first()

def update_tax_rule(db: Session, tax_id: int, update: TaxRuleUpdate):
    db_tax = get_tax_rule(db, tax_id)
    if not db_tax:
        return None
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tax, key, value)
    db.commit()
    db.refresh(db_tax)
    return db_tax

def delete_tax_rule(db: Session, tax_id: int):
    db_tax = get_tax_rule(db, tax_id)
    if not db_tax:
        return False
    db.delete(db_tax)
    db.commit()
    return True

def get_audit_logs(db: Session, skip: int = 0, limit: int = 200):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

# ============== FASTAPI APP ==============
app = FastAPI(
    title="ShopSwift E-Commerce API",
    description="FastAPI backend for ShopSwift e-commerce application",
    version="2.1.0"
)

# ============== CORS MIDDLEWARE ==============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== STATIC FILES ==============
frontend_assets = os.path.join(os.path.dirname(__file__), "..", "ecommerc-app", "src", "assets")
if os.path.exists(frontend_assets):
    app.mount("/assets", StaticFiles(directory=frontend_assets), name="assets")

ADMIN_SECRET_KEY = "ADMIN123"

# ============== ROOT ENDPOINT ==============
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to ShopSwift API",
        "docs": "/docs",
        "version": "2.1.0"
    }

# ============== USER ENDPOINTS ==============
@app.post("/api/register", response_model=UserResponse, tags=["Users"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user. Provide admin_key to register as admin."""
    strength = check_password_strength(user.password)
    if not strength["valid"]:
        raise HTTPException(status_code=400, detail=strength["message"])
    is_admin = 0
    if user.admin_key:
        if user.admin_key == ADMIN_SECRET_KEY:
            is_admin = 1
        else:
            raise HTTPException(status_code=403, detail="Invalid admin key")
    return create_user(db=db, user=user, is_admin=is_admin)

@app.post("/api/login", response_model=Token, tags=["Users"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_banned:
        raise HTTPException(status_code=403, detail="Account has been banned")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me", response_model=UserResponse, tags=["Users"])
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current logged-in user details"""
    return current_user

# ============== 2FA ENDPOINTS ==============
@app.post("/api/2fa/setup", tags=["2FA"])
def setup_2fa(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Generate TOTP secret and provisioning URI for QR code"""
    secret = generate_totp_secret()
    current_user.two_factor_secret = secret
    current_user.two_factor_enabled = 0
    db.commit()
    uri = get_totp_uri(secret, current_user.email)
    return {"secret": secret, "uri": uri}

@app.post("/api/2fa/verify", tags=["2FA"])
def verify_2fa_setup(token: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Verify initial TOTP token and enable 2FA"""
    if not current_user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA not set up")
    if verify_totp(current_user.two_factor_secret, token):
        current_user.two_factor_enabled = 1
        db.commit()
        return {"message": "2FA enabled successfully"}
    raise HTTPException(status_code=400, detail="Invalid OTP")

@app.post("/api/2fa/login-verify", response_model=Token, tags=["2FA"])
def login_2fa_verify(email: str, password: str, token: str, db: Session = Depends(get_db)):
    """Login with 2FA verification step"""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled for this user")
    if not verify_totp(user.two_factor_secret, token):
        raise HTTPException(status_code=401, detail="Invalid OTP")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# ============== PRODUCT ENDPOINTS ==============
@app.get("/api/products", response_model=List[ProductResponse], tags=["Products"])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional category filter"""
    return get_products(db, skip=skip, limit=limit, category=category)

@app.get("/api/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@app.post("/api/products", response_model=ProductResponse, tags=["Products"])
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Add a new product (admin only)"""
    db_product = create_product(db=db, product=product)
    log_audit_action(db, current_user.id, "CREATE", "Product", db_product.id, f"Created product {db_product.title}")
    return db_product

@app.put("/api/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def update_existing_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a product (admin only)"""
    db_product = update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    log_audit_action(db, current_user.id, "UPDATE", "Product", db_product.id, f"Updated product {db_product.title}")
    return db_product

@app.delete("/api/products/{product_id}", response_model=Message, tags=["Products"])
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a product (admin only)"""
    product = delete_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    log_audit_action(db, current_user.id, "DELETE", "Product", product_id, f"Deleted product {product.title}")
    return {"message": "Product deleted successfully"}

# ============== ADMIN PRODUCT ENDPOINTS ==============
@app.get("/api/admin/products", response_model=List[ProductResponse], tags=["Admin"])
def read_admin_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all products with admin filters (admin only)"""
    return get_products(db, skip=skip, limit=limit, category=category, status=status)

# ============== CART ENDPOINTS ==============
@app.get("/api/cart", response_model=List[CartResponse], tags=["Cart"])
def read_cart(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get all cart items for current user"""
    return get_cart_items(db, current_user.id)

@app.post("/api/cart", response_model=CartResponse, tags=["Cart"])
def add_item_to_cart(
    cart: CartCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a product to cart"""
    return add_to_cart(db, current_user.id, cart)

@app.put("/api/cart/{cart_id}", response_model=CartResponse, tags=["Cart"])
def update_cart_quantity(
    cart_id: int,
    item: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update quantity of a cart item"""
    cart_item = update_cart_item(db, cart_id, current_user.id, item.quantity)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    return cart_item

@app.delete("/api/cart/{cart_id}", response_model=Message, tags=["Cart"])
def remove_cart_item(
    cart_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a single item from cart"""
    success = remove_from_cart(db, cart_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    return {"message": "Item removed from cart"}

@app.delete("/api/cart", response_model=Message, tags=["Cart"])
def clear_user_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear entire cart for current user"""
    clear_cart(db, current_user.id)
    return {"message": "Cart cleared successfully"}

# ============== SEARCH ENDPOINTS ==============
@app.get("/api/search", response_model=List[ProductResponse], tags=["Search"])
def search(
    q: str,
    db: Session = Depends(get_db)
):
    """Search products by title, description, or category"""
    return search_products(db, q)

# ============== REVIEW ENDPOINTS ==============
@app.get("/api/products/{product_id}/reviews", response_model=List[ReviewResponse], tags=["Reviews"])
def read_reviews(product_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a product"""
    reviews = get_reviews(db, product_id)
    result = []
    for r in reviews:
        result.append({
            "id": r.id,
            "user_id": r.user_id,
            "product_id": r.product_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at,
            "user_name": r.user.name if r.user else None
        })
    return result

@app.post("/api/reviews", response_model=ReviewResponse, tags=["Reviews"])
def add_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a review to a product"""
    db_review = create_review(db, current_user.id, review)
    return {
        "id": db_review.id,
        "user_id": db_review.user_id,
        "product_id": db_review.product_id,
        "rating": db_review.rating,
        "comment": db_review.comment,
        "created_at": db_review.created_at,
        "user_name": current_user.name
    }

@app.delete("/api/reviews/{review_id}", response_model=Message, tags=["Reviews"])
def remove_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete own review"""
    success = delete_review(db, review_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return {"message": "Review deleted"}

# ============== WISHLIST ENDPOINTS ==============
@app.get("/api/wishlist", response_model=List[WishlistResponse], tags=["Wishlist"])
def read_wishlist(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's wishlist"""
    return get_wishlist(db, current_user.id)

@app.post("/api/wishlist/{product_id}", response_model=WishlistResponse, tags=["Wishlist"])
def add_wishlist_item(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add product to wishlist"""
    return add_to_wishlist(db, current_user.id, product_id)

@app.delete("/api/wishlist/{wishlist_id}", response_model=Message, tags=["Wishlist"])
def remove_wishlist_item(
    wishlist_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove item from wishlist"""
    success = remove_from_wishlist(db, wishlist_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    return {"message": "Removed from wishlist"}

# ============== ORDER ENDPOINTS ==============
@app.post("/api/orders", response_model=OrderResponse, tags=["Orders"])
def place_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Place a new order from cart items"""
    db_order = create_order(db, current_user.id, order)
    clear_cart(db, current_user.id)
    return db_order

@app.get("/api/orders/my", response_model=List[OrderListResponse], tags=["Orders"])
def read_my_orders(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's order history"""
    orders = get_user_orders(db, current_user.id)
    return [
        {
            "id": o.id,
            "status": o.status,
            "total": float(o.total),
            "created_at": o.created_at,
            "item_count": len(o.items)
        }
        for o in orders
    ]

@app.get("/api/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def read_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order details by ID (owner or admin)"""
    db_order = get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.user_id != current_user.id and current_user.role not in ("admin", "manager") and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return db_order

@app.get("/api/orders", response_model=List[OrderListResponse], tags=["Admin"])
def read_all_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all orders (admin only)"""
    orders = get_all_orders(db, skip, limit)
    return [
        {
            "id": o.id,
            "status": o.status,
            "total": float(o.total),
            "created_at": o.created_at,
            "item_count": len(o.items)
        }
        for o in orders
    ]

@app.put("/api/orders/{order_id}/status", response_model=OrderResponse, tags=["Admin"])
def update_order(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    db_order = update_order_status(db, order_id, status_update)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    log_audit_action(db, current_user.id, "UPDATE", "Order", db_order.id, f"Status changed to {status_update.status}")
    return db_order

@app.post("/api/admin/orders/draft", response_model=OrderResponse, tags=["Admin"])
def draft_order(
    order: DraftOrderCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a draft order manually (admin only)"""
    db_order = create_draft_order(db, order)
    log_audit_action(db, current_user.id, "CREATE", "Order", db_order.id, "Created draft order")
    return db_order

@app.post("/api/admin/orders/{order_id}/cancel", response_model=OrderResponse, tags=["Admin"])
def cancel_existing_order(
    order_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Cancel an order (admin only)"""
    db_order = cancel_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    log_audit_action(db, current_user.id, "UPDATE", "Order", db_order.id, "Cancelled order")
    return db_order

@app.post("/api/admin/orders/{order_id}/refund", response_model=OrderResponse, tags=["Admin"])
def refund_existing_order(
    order_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Refund a delivered order (admin only)"""
    db_order = refund_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    log_audit_action(db, current_user.id, "UPDATE", "Order", db_order.id, "Refunded order")
    return db_order

# ============== COUPON ENDPOINTS ==============
@app.post("/api/coupons", response_model=CouponResponse, tags=["Admin"])
def create_new_coupon(
    coupon: CouponCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new coupon (admin only)"""
    db_coupon = create_coupon(db, coupon)
    log_audit_action(db, current_user.id, "CREATE", "Coupon", db_coupon.id, f"Created coupon {db_coupon.code}")
    return db_coupon

@app.get("/api/coupons", response_model=List[CouponResponse], tags=["Coupons"])
def read_coupons(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all coupons (admin only)"""
    return get_all_coupons(db)

@app.post("/api/coupons/validate", response_model=CouponApplyResponse, tags=["Coupons"])
def validate_coupon_code(
    data: CouponValidate,
    db: Session = Depends(get_db)
):
    """Validate a coupon code and return discount"""
    result = validate_coupon(db, data.code, data.order_total)
    return result

@app.delete("/api/coupons/{coupon_id}", response_model=Message, tags=["Admin"])
def remove_coupon(
    coupon_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a coupon (admin only)"""
    success = delete_coupon(db, coupon_id)
    if not success:
        raise HTTPException(status_code=404, detail="Coupon not found")
    log_audit_action(db, current_user.id, "DELETE", "Coupon", coupon_id, "Deleted coupon")
    return {"message": "Coupon deleted"}

# ============== INVENTORY ENDPOINTS ==============
@app.put("/api/products/{product_id}/inventory", response_model=ProductResponse, tags=["Admin"])
def update_product_inventory(
    product_id: int,
    data: InventoryUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update product stock quantity (admin only)"""
    product = update_inventory(db, product_id, data.stock_quantity, data.low_stock_threshold)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    log_audit_action(db, current_user.id, "UPDATE", "Product", product.id, f"Inventory updated to {data.stock_quantity}")
    return product

@app.get("/api/inventory/low-stock", response_model=List[LowStockResponse], tags=["Admin"])
def read_low_stock(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get products with low stock (admin only)"""
    products = get_low_stock_products(db)
    return [
        {
            "id": p.id,
            "title": p.title,
            "stock_quantity": p.stock_quantity,
            "low_stock_threshold": p.low_stock_threshold,
            "category": p.category
        }
        for p in products
    ]

# ============== ADMIN USER MANAGEMENT ENDPOINTS ==============
@app.get("/api/admin/users", response_model=List[UserResponse], tags=["Admin"])
def read_all_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    return get_users(db, skip=skip, limit=limit, search=search)

@app.post("/api/admin/users", response_model=UserResponse, tags=["Admin"])
def create_user_admin(
    user: UserAdminCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user from admin panel (admin only)"""
    db_user = create_admin_user(db, user)
    log_audit_action(db, current_user.id, "CREATE", "User", db_user.id, f"Created user {db_user.email}")
    return db_user

@app.put("/api/admin/users/{user_id}", response_model=UserResponse, tags=["Admin"])
def update_user(
    user_id: int,
    update: UserAdminUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a user (admin only)"""
    db_user = update_user_admin(db, user_id, update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    log_audit_action(db, current_user.id, "UPDATE", "User", db_user.id, f"Updated user {db_user.email}")
    return db_user

@app.delete("/api/admin/users/{user_id}", response_model=Message, tags=["Admin"])
def delete_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    log_audit_action(db, current_user.id, "DELETE", "User", user_id, "Deleted user")
    return {"message": "User deleted"}

@app.post("/api/admin/users/{user_id}/ban", response_model=UserResponse, tags=["Admin"])
def ban_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Ban a user (admin only)"""
    db_user = ban_user(db, user_id, banned=True)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    log_audit_action(db, current_user.id, "BAN", "User", db_user.id, f"Banned user {db_user.email}")
    return db_user

@app.post("/api/admin/users/{user_id}/unban", response_model=UserResponse, tags=["Admin"])
def unban_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Unban a user (admin only)"""
    db_user = ban_user(db, user_id, banned=False)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    log_audit_action(db, current_user.id, "UNBAN", "User", db_user.id, f"Unbanned user {db_user.email}")
    return db_user

# ============== CATEGORY ENDPOINTS ==============
@app.get("/api/admin/categories", response_model=List[CategoryResponse], tags=["Admin"])
def read_categories(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all categories (admin only)"""
    return get_categories(db)

@app.post("/api/admin/categories", response_model=CategoryResponse, tags=["Admin"])
def create_new_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new category (admin only)"""
    db_cat = create_category(db, category)
    log_audit_action(db, current_user.id, "CREATE", "Category", db_cat.id, f"Created category {db_cat.name}")
    return db_cat

@app.put("/api/admin/categories/{category_id}", response_model=CategoryResponse, tags=["Admin"])
def update_existing_category(
    category_id: int,
    update: CategoryUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a category (admin only)"""
    db_cat = update_category(db, category_id, update)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    log_audit_action(db, current_user.id, "UPDATE", "Category", db_cat.id, f"Updated category {db_cat.name}")
    return db_cat

@app.delete("/api/admin/categories/{category_id}", response_model=Message, tags=["Admin"])
def delete_existing_category(
    category_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a category (admin only)"""
    success = delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    log_audit_action(db, current_user.id, "DELETE", "Category", category_id, "Deleted category")
    return {"message": "Category deleted"}

# ============== TAX RULE ENDPOINTS ==============
@app.get("/api/admin/tax-rules", response_model=List[TaxRuleResponse], tags=["Admin"])
def read_tax_rules(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all tax rules (admin only)"""
    return get_tax_rules(db)

@app.post("/api/admin/tax-rules", response_model=TaxRuleResponse, tags=["Admin"])
def create_new_tax_rule(
    tax: TaxRuleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new tax rule (admin only)"""
    db_tax = create_tax_rule(db, tax)
    log_audit_action(db, current_user.id, "CREATE", "TaxRule", db_tax.id, f"Created tax rule {db_tax.name}")
    return db_tax

@app.put("/api/admin/tax-rules/{tax_id}", response_model=TaxRuleResponse, tags=["Admin"])
def update_existing_tax_rule(
    tax_id: int,
    update: TaxRuleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a tax rule (admin only)"""
    db_tax = update_tax_rule(db, tax_id, update)
    if not db_tax:
        raise HTTPException(status_code=404, detail="Tax rule not found")
    log_audit_action(db, current_user.id, "UPDATE", "TaxRule", db_tax.id, f"Updated tax rule {db_tax.name}")
    return db_tax

@app.delete("/api/admin/tax-rules/{tax_id}", response_model=Message, tags=["Admin"])
def delete_existing_tax_rule(
    tax_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a tax rule (admin only)"""
    success = delete_tax_rule(db, tax_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tax rule not found")
    log_audit_action(db, current_user.id, "DELETE", "TaxRule", tax_id, "Deleted tax rule")
    return {"message": "Tax rule deleted"}

# ============== AUDIT LOG ENDPOINTS ==============
@app.get("/api/admin/audit-logs", response_model=List[AuditLogResponse], tags=["Admin"])
def read_audit_logs(
    skip: int = 0,
    limit: int = 200,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)"""
    logs = get_audit_logs(db, skip=skip, limit=limit)
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_name": log.user.name if log.user else None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "created_at": log.created_at
        }
        for log in logs
    ]

# ============== ADMIN ANALYTICS ENDPOINT ==============
@app.get("/api/admin/analytics", response_model=AdminAnalytics, tags=["Admin"])
def admin_analytics(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard analytics (admin only)"""
    summary = get_sales_summary(db)
    top = get_top_products(db, limit=5)
    recent = get_recent_orders(db, limit=10)
    low_stock = get_low_stock_products(db)

    return {
        "sales_summary": summary,
        "top_products": top,
        "recent_orders": [
            {
                "id": o.id,
                "status": o.status,
                "total": float(o.total),
                "created_at": o.created_at,
                "item_count": len(o.items)
            }
            for o in recent
        ],
        "low_stock_items": [
            {
                "id": p.id,
                "title": p.title,
                "stock_quantity": p.stock_quantity,
                "low_stock_threshold": p.low_stock_threshold,
                "category": p.category
            }
            for p in low_stock
        ]
    }

# ============== RUN SERVER ==============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)