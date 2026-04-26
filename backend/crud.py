from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime
from sqlalchemy import func, desc

from models import (
    User, Product, Cart, Review, Wishlist, Order, OrderItem, Coupon,
    Category, TaxRule, AuditLog, UserRole
)
from schemas import (
    UserCreate, ProductCreate, ProductUpdate, CartCreate, ReviewCreate,
    OrderCreate, OrderStatusUpdate, CouponCreate, CouponValidate,
    UserAdminCreate, UserAdminUpdate, CategoryCreate, CategoryUpdate,
    TaxRuleCreate, TaxRuleUpdate, DraftOrderCreate
)
from auth import get_password_hash


# ============== AUDIT LOG ==============

def log_audit_action(db: Session, user_id: int, action: str, entity_type: str, entity_id: Optional[int] = None, details: Optional[str] = None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        created_at=datetime.utcnow()
    )
    db.add(log)
    db.commit()


# ============== USER CRUD ==============

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[User]:
    query = db.query(User)
    if search:
        s = f"%{search}%"
        query = query.filter(User.name.ilike(s) | User.email.ilike(s))
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate, is_admin: int = 0) -> User:
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    role = UserRole.ADMIN.value if is_admin else UserRole.CUSTOMER.value
    db_user = User(
        name=user.name,
        email=user.email,
        address=user.address,
        mobile=user.mobile,
        hashed_password=hashed_password,
        is_admin=is_admin,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_admin_user(db: Session, user: UserAdminCreate) -> User:
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        address=user.address,
        mobile=user.mobile,
        hashed_password=hashed_password,
        role=user.role,
        is_admin=1 if user.role == UserRole.ADMIN.value else 0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_admin(db: Session, user_id: int, update: UserAdminUpdate) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    data = update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_user, field, value)
    if "role" in data:
        db_user.is_admin = 1 if data["role"] == UserRole.ADMIN.value else 0
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def ban_user(db: Session, user_id: int, banned: bool = True) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db_user.is_banned = 1 if banned else 0
    db.commit()
    db.refresh(db_user)
    return db_user


# ============== PRODUCT CRUD ==============

def get_products(db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None, status: Optional[str] = None) -> List[Product]:
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Product.status == status)
    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_slug(db: Session, slug: str) -> Optional[Product]:
    return db.query(Product).filter(Product.slug == slug).first()


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> Optional[Product]:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product


# ============== CART CRUD ==============

def get_cart_items(db: Session, user_id: int) -> List[Cart]:
    return db.query(Cart).filter(Cart.user_id == user_id).all()


def get_cart_item(db: Session, user_id: int, product_id: int) -> Optional[Cart]:
    return db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == product_id).first()


def add_to_cart(db: Session, user_id: int, cart: CartCreate) -> Cart:
    product = db.query(Product).filter(Product.id == cart.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    if product.stock_quantity < cart.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.stock_quantity} items available in stock"
        )

    db_cart = get_cart_item(db, user_id, cart.product_id)
    if db_cart:
        new_qty = db_cart.quantity + cart.quantity
        if product.stock_quantity < new_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.stock_quantity} items available in stock"
            )
        db_cart.quantity = new_qty
    else:
        db_cart = Cart(
            user_id=user_id,
            product_id=cart.product_id,
            quantity=cart.quantity
        )
        db.add(db_cart)

    db.commit()
    db.refresh(db_cart)
    return db_cart


def update_cart_item(db: Session, cart_id: int, user_id: int, quantity: int) -> Optional[Cart]:
    db_cart = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id).first()
    if not db_cart:
        return None
    product = db_cart.product
    if product.stock_quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.stock_quantity} items available in stock"
        )
    db_cart.quantity = quantity
    db.commit()
    db.refresh(db_cart)
    return db_cart


def remove_from_cart(db: Session, cart_id: int, user_id: int) -> bool:
    db_cart = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id).first()
    if not db_cart:
        return False
    db.delete(db_cart)
    db.commit()
    return True


def clear_cart(db: Session, user_id: int) -> None:
    db.query(Cart).filter(Cart.user_id == user_id).delete()
    db.commit()


# ============== REVIEW CRUD ==============

def get_reviews(db: Session, product_id: int) -> List[Review]:
    return db.query(Review).filter(Review.product_id == product_id).all()


def get_review(db: Session, review_id: int) -> Optional[Review]:
    return db.query(Review).filter(Review.id == review_id).first()


def create_review(db: Session, user_id: int, review: ReviewCreate) -> Review:
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
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


def delete_review(db: Session, review_id: int, user_id: int) -> bool:
    db_review = db.query(Review).filter(Review.id == review_id, Review.user_id == user_id).first()
    if not db_review:
        return False
    db.delete(db_review)
    db.commit()
    return True


# ============== WISHLIST CRUD ==============

def get_wishlist(db: Session, user_id: int) -> List[Wishlist]:
    return db.query(Wishlist).filter(Wishlist.user_id == user_id).all()


def add_to_wishlist(db: Session, user_id: int, product_id: int) -> Wishlist:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    existing = db.query(Wishlist).filter(Wishlist.user_id == user_id, Wishlist.product_id == product_id).first()
    if existing:
        return existing
    db_wish = Wishlist(user_id=user_id, product_id=product_id)
    db.add(db_wish)
    db.commit()
    db.refresh(db_wish)
    return db_wish


def remove_from_wishlist(db: Session, wishlist_id: int, user_id: int) -> bool:
    db_wish = db.query(Wishlist).filter(Wishlist.id == wishlist_id, Wishlist.user_id == user_id).first()
    if not db_wish:
        return False
    db.delete(db_wish)
    db.commit()
    return True


# ============== SEARCH ==============

def search_products(db: Session, query: str) -> List[Product]:
    search = f"%{query}%"
    return db.query(Product).filter(
        Product.title.ilike(search) | Product.description.ilike(search) | Product.category.ilike(search)
    ).all()


# ============== ORDER CRUD ==============

def create_order(db: Session, user_id: Optional[int], order_data: OrderCreate) -> Order:
    subtotal = sum(item.unit_price * item.quantity for item in order_data.items)
    tax = round(subtotal * 0.18, 2)
    discount = 0.0

    if order_data.coupon_code:
        coupon = db.query(Coupon).filter(Coupon.code == order_data.coupon_code.upper(), Coupon.is_active == 1).first()
        if coupon and coupon.valid_until and coupon.valid_until < datetime.utcnow():
            coupon = None
        if coupon and coupon.usage_count >= coupon.usage_limit:
            coupon = None
        if coupon and subtotal < float(coupon.min_order_value or 0):
            coupon = None
        if coupon:
            if coupon.coupon_type == "percentage":
                discount = round(subtotal * float(coupon.value) / 100, 2)
                if coupon.max_discount and discount > float(coupon.max_discount):
                    discount = float(coupon.max_discount)
            elif coupon.coupon_type == "fixed":
                discount = float(coupon.value)
                if discount > subtotal:
                    discount = subtotal
            elif coupon.coupon_type == "bogo":
                discount = 0
            coupon.usage_count += 1

    total = round(subtotal + tax - discount, 2)
    if total < 0:
        total = 0

    db_order = Order(
        user_id=user_id,
        guest_email=order_data.guest_email,
        guest_name=order_data.guest_name,
        guest_mobile=order_data.guest_mobile,
        guest_address=order_data.guest_address,
        status="pending",
        payment_method=order_data.payment_method,
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        total=total,
        coupon_code=order_data.coupon_code.upper() if order_data.coupon_code else None,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.title}. Available: {product.stock_quantity}"
            )
        product.stock_quantity -= item.quantity
        db_order_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(db_order_item)

    db.commit()
    db.refresh(db_order)
    return db_order


def create_draft_order(db: Session, order_data: DraftOrderCreate) -> Order:
    subtotal = sum(item.unit_price * item.quantity for item in order_data.items)
    tax = round(subtotal * 0.18, 2)
    discount = 0.0

    if order_data.coupon_code:
        coupon = db.query(Coupon).filter(Coupon.code == order_data.coupon_code.upper(), Coupon.is_active == 1).first()
        if coupon and coupon.valid_until and coupon.valid_until < datetime.utcnow():
            coupon = None
        if coupon and coupon.usage_count >= coupon.usage_limit:
            coupon = None
        if coupon and subtotal < float(coupon.min_order_value or 0):
            coupon = None
        if coupon:
            if coupon.coupon_type == "percentage":
                discount = round(subtotal * float(coupon.value) / 100, 2)
                if coupon.max_discount and discount > float(coupon.max_discount):
                    discount = float(coupon.max_discount)
            elif coupon.coupon_type == "fixed":
                discount = float(coupon.value)
                if discount > subtotal:
                    discount = subtotal
            elif coupon.coupon_type == "bogo":
                discount = 0
            coupon.usage_count += 1

    total = round(subtotal + tax - discount, 2)
    if total < 0:
        total = 0

    db_order = Order(
        user_id=order_data.user_id,
        guest_email=order_data.guest_email,
        guest_name=order_data.guest_name,
        guest_mobile=order_data.guest_mobile,
        guest_address=order_data.guest_address,
        status="pending",
        payment_method=order_data.payment_method,
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        total=total,
        coupon_code=order_data.coupon_code.upper() if order_data.coupon_code else None,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        db_order_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(db_order_item)

    db.commit()
    db.refresh(db_order)
    return db_order


def cancel_order(db: Session, order_id: int) -> Optional[Order]:
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None
    if db_order.status in ["shipped", "delivered"]:
        raise HTTPException(status_code=400, detail="Cannot cancel shipped or delivered order")
    db_order.status = "cancelled"
    # Restore stock
    for item in db_order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity
    db.commit()
    db.refresh(db_order)
    return db_order


def refund_order(db: Session, order_id: int) -> Optional[Order]:
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None
    if db_order.status != "delivered":
        raise HTTPException(status_code=400, detail="Only delivered orders can be refunded")
    db_order.status = "cancelled"
    for item in db_order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()


def get_user_orders(db: Session, user_id: int) -> List[Order]:
    return db.query(Order).filter(Order.user_id == user_id).order_by(desc(Order.created_at)).all()


def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()


def update_order_status(db: Session, order_id: int, status_update: OrderStatusUpdate) -> Optional[Order]:
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None
    db_order.status = status_update.status
    db.commit()
    db.refresh(db_order)
    return db_order


# ============== COUPON CRUD ==============

def create_coupon(db: Session, coupon: CouponCreate) -> Coupon:
    existing = db.query(Coupon).filter(Coupon.code == coupon.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    db_coupon = Coupon(
        code=coupon.code.upper(),
        coupon_type=coupon.coupon_type,
        value=coupon.value,
        min_order_value=coupon.min_order_value or 0,
        max_discount=coupon.max_discount,
        usage_limit=coupon.usage_limit or 1,
        valid_from=coupon.valid_from or datetime.utcnow(),
        valid_until=coupon.valid_until,
        is_active=1
    )
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


def get_coupon_by_code(db: Session, code: str) -> Optional[Coupon]:
    return db.query(Coupon).filter(Coupon.code == code.upper()).first()


def get_all_coupons(db: Session) -> List[Coupon]:
    return db.query(Coupon).order_by(desc(Coupon.created_at)).all()


def delete_coupon(db: Session, coupon_id: int) -> bool:
    db_coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not db_coupon:
        return False
    db.delete(db_coupon)
    db.commit()
    return True


def validate_coupon(db: Session, code: str, order_total: float) -> dict:
    coupon = get_coupon_by_code(db, code)
    if not coupon:
        return {"valid": False, "discount": 0, "message": "Invalid coupon code"}
    if not coupon.is_active:
        return {"valid": False, "discount": 0, "message": "Coupon is inactive"}
    if coupon.valid_until and coupon.valid_until < datetime.utcnow():
        return {"valid": False, "discount": 0, "message": "Coupon has expired"}
    if coupon.usage_count >= coupon.usage_limit:
        return {"valid": False, "discount": 0, "message": "Coupon usage limit reached"}
    if order_total < float(coupon.min_order_value or 0):
        return {"valid": False, "discount": 0, "message": f"Minimum order value of ₹{coupon.min_order_value} required"}

    discount = 0.0
    if coupon.coupon_type == "percentage":
        discount = round(order_total * float(coupon.value) / 100, 2)
        if coupon.max_discount and discount > float(coupon.max_discount):
            discount = float(coupon.max_discount)
    elif coupon.coupon_type == "fixed":
        discount = float(coupon.value)
        if discount > order_total:
            discount = order_total
    elif coupon.coupon_type == "bogo":
        discount = 0

    return {"valid": True, "discount": discount, "message": f"Coupon applied! You save ₹{discount}"}


# ============== CATEGORY CRUD ==============

def create_category(db: Session, category: CategoryCreate) -> Category:
    existing = db.query(Category).filter(Category.slug == category.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category slug already exists")
    db_cat = Category(**category.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


def get_categories(db: Session) -> List[Category]:
    return db.query(Category).order_by(Category.name).all()


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def update_category(db: Session, category_id: int, update: CategoryUpdate) -> Optional[Category]:
    db_cat = db.query(Category).filter(Category.id == category_id).first()
    if not db_cat:
        return None
    data = update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_cat, field, value)
    db_cat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_cat)
    return db_cat


def delete_category(db: Session, category_id: int) -> bool:
    db_cat = db.query(Category).filter(Category.id == category_id).first()
    if not db_cat:
        return False
    # Check if category has children
    children = db.query(Category).filter(Category.parent_id == category_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with subcategories")
    db.delete(db_cat)
    db.commit()
    return True


# ============== TAX RULE CRUD ==============

def create_tax_rule(db: Session, tax: TaxRuleCreate) -> TaxRule:
    db_tax = TaxRule(**tax.model_dump())
    db.add(db_tax)
    db.commit()
    db.refresh(db_tax)
    return db_tax


def get_tax_rules(db: Session) -> List[TaxRule]:
    return db.query(TaxRule).order_by(TaxRule.name).all()


def get_tax_rule(db: Session, tax_id: int) -> Optional[TaxRule]:
    return db.query(TaxRule).filter(TaxRule.id == tax_id).first()


def update_tax_rule(db: Session, tax_id: int, update: TaxRuleUpdate) -> Optional[TaxRule]:
    db_tax = db.query(TaxRule).filter(TaxRule.id == tax_id).first()
    if not db_tax:
        return None
    data = update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_tax, field, value)
    db_tax.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_tax)
    return db_tax


def delete_tax_rule(db: Session, tax_id: int) -> bool:
    db_tax = db.query(TaxRule).filter(TaxRule.id == tax_id).first()
    if not db_tax:
        return False
    db.delete(db_tax)
    db.commit()
    return True


# ============== AUDIT LOG CRUD ==============

def get_audit_logs(db: Session, skip: int = 0, limit: int = 200) -> List[AuditLog]:
    return db.query(AuditLog).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()


# ============== INVENTORY / ANALYTICS ==============

def update_inventory(db: Session, product_id: int, stock_quantity: int, low_stock_threshold: Optional[int] = None) -> Optional[Product]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    product.stock_quantity = stock_quantity
    if low_stock_threshold is not None:
        product.low_stock_threshold = low_stock_threshold
    db.commit()
    db.refresh(product)
    return product


def get_low_stock_products(db: Session) -> List[Product]:
    return db.query(Product).filter(Product.stock_quantity <= Product.low_stock_threshold).all()


def get_sales_summary(db: Session) -> dict:
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.sum(Order.total)).scalar() or 0
    total_customers = db.query(User).count()
    avg_order = db.query(func.avg(Order.total)).scalar() or 0
    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "total_customers": total_customers,
        "average_order_value": round(float(avg_order), 2)
    }


def get_top_products(db: Session, limit: int = 5) -> List[dict]:
    results = db.query(
        Product.id.label("product_id"),
        Product.title,
        func.sum(OrderItem.quantity).label("total_sold"),
        func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue")
    ).join(OrderItem, Product.id == OrderItem.product_id).group_by(Product.id).order_by(desc("total_sold")).limit(limit).all()

    return [
        {
            "product_id": r.product_id,
            "title": r.title,
            "total_sold": int(r.total_sold or 0),
            "total_revenue": float(r.total_revenue or 0)
        }
        for r in results
    ]


def get_recent_orders(db: Session, limit: int = 10) -> List[Order]:
    return db.query(Order).order_by(desc(Order.created_at)).limit(limit).all()

