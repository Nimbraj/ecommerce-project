import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from database import SessionLocal, engine, Base
from models import Product, User
from crud import create_product
from schemas import ProductCreate
from auth import get_password_hash


def seed_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_email = os.getenv("INITIAL_ADMIN_EMAIL")
        admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")
        if not admin_email or not admin_password:
            print("Administrator bootstrap skipped; configure INITIAL_ADMIN_EMAIL and INITIAL_ADMIN_PASSWORD")
            return

        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin = User(
                name=os.getenv("INITIAL_ADMIN_NAME", "Store Administrator"),
                email=admin_email,
                address="456 Admin Avenue, City",
                mobile="9876543211",
                hashed_password=get_password_hash(admin_password),
                is_admin=1
            )
            db.add(admin)
            db.commit()
            print(f"Added configured administrator: {admin_email}")
        else:
            print("Configured administrator already exists")
    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        db.close()


def seed_products():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    products = [
        {"title": "Wireless Headphones", "description": "Premium wireless headphones with noise cancellation and 20-hour battery life.", "price": 3999.0, "category": "Electronics", "image_url": "/assets/21.jpg", "is_featured": 1, "stock_quantity": 45},
        {"title": "Smart Watch", "description": "Stay connected and track your health with this advanced smart watch.", "price": 2999.0, "category": "Electronics", "image_url": "/assets/22.jpg", "is_featured": 1, "stock_quantity": 30},
        {"title": "Bluetooth Speaker", "description": "Compact and waterproof speaker with deep bass and long battery life.", "price": 1499.0, "category": "Electronics", "image_url": "/assets/23.jpg", "is_featured": 0, "stock_quantity": 60},
        {"title": "DSLR Camera", "description": "Professional-quality DSLR camera for stunning photography and video.", "price": 25999.0, "category": "Electronics", "image_url": "/assets/24.jpg", "is_featured": 1, "stock_quantity": 12},
        {"title": "Gaming Mouse", "description": "High-precision gaming mouse with customizable buttons and RGB lighting.", "price": 999.0, "category": "Gaming", "image_url": "/assets/25.jpg", "is_featured": 0, "stock_quantity": 80},
        {"title": "Mechanical Keyboard", "description": "Durable mechanical keyboard with tactile feedback and backlit keys.", "price": 2199.0, "category": "Gaming", "image_url": "/assets/26.jpg", "is_featured": 0, "stock_quantity": 55},
        {"title": "4K Monitor", "description": "Ultra HD 4K monitor with vibrant colors and sharp display for professionals.", "price": 19999.0, "category": "Electronics", "image_url": "/assets/27.jpg", "is_featured": 1, "stock_quantity": 18},
        {"title": "Noise Cancelling Earbuds", "description": "Compact earbuds with active noise cancelling and long battery life.", "price": 1799.0, "category": "Electronics", "image_url": "/assets/28.jpg", "is_featured": 0, "stock_quantity": 70},
        {"title": "Portable Charger", "description": "High-capacity 20000mAh power bank with fast charging support.", "price": 1299.0, "category": "Electronics", "image_url": "/assets/1.jpg", "is_featured": 0, "stock_quantity": 100},
        {"title": "Fitness Tracker", "description": "Lightweight fitness band with heart rate monitor and sleep tracking.", "price": 1499.0, "category": "Electronics", "image_url": "/assets/2.jpg", "is_featured": 0, "stock_quantity": 65},
        {"title": "Drone with Camera", "description": "Easy-to-fly drone with 4K camera and GPS stabilization.", "price": 8999.0, "category": "Electronics", "image_url": "/assets/3.jpg", "is_featured": 1, "stock_quantity": 15},
        {"title": "VR Headset", "description": "Immersive virtual reality headset for gaming and media.", "price": 4999.0, "category": "Gaming", "image_url": "/assets/4.jpg", "is_featured": 1, "stock_quantity": 22},
        {"title": "Action Camera", "description": "Rugged waterproof action camera for adventure sports.", "price": 6999.0, "category": "Electronics", "image_url": "/assets/5.jpg", "is_featured": 0, "stock_quantity": 28},
        {"title": "Smart Home Hub", "description": "Control all your smart devices from one central hub.", "price": 3499.0, "category": "Electronics", "image_url": "/assets/7.png", "is_featured": 0, "stock_quantity": 40},
        {"title": "Wireless Earphones", "description": "True wireless earphones with deep bass and touch controls.", "price": 899.0, "category": "Electronics", "image_url": "/assets/8.jpg", "is_featured": 0, "stock_quantity": 90},
        {"title": "Bestselling Novel", "description": "A gripping storyline that keeps you hooked till the last page.", "price": 399.0, "category": "Books", "image_url": "/assets/9.jpg", "is_featured": 0, "stock_quantity": 120},
        {"title": "Coffee Maker", "description": "Brew barista-quality coffee at home with this compact machine.", "price": 2499.0, "category": "Appliances", "image_url": "/assets/10.jpg", "is_featured": 0, "stock_quantity": 35},
        {"title": "Running Shoes", "description": "Lightweight cushioned running shoes for daily workouts.", "price": 1999.0, "category": "Fashion", "image_url": "/assets/11.jpg", "is_featured": 1, "stock_quantity": 50},
        {"title": "Yoga Mat", "description": "Non-slip eco-friendly yoga mat with carrying strap.", "price": 599.0, "category": "Sports", "image_url": "/assets/12.jpg", "is_featured": 0, "stock_quantity": 75},
        {"title": "Backpack", "description": "Durable water-resistant backpack with laptop compartment.", "price": 1299.0, "category": "Fashion", "image_url": "/assets/13.jpg", "is_featured": 0, "stock_quantity": 60},
        {"title": "Sunglasses", "description": "UV-protected polarized sunglasses with premium frames.", "price": 899.0, "category": "Fashion", "image_url": "/assets/14.jpg", "is_featured": 0, "stock_quantity": 85},
        {"title": "Water Bottle", "description": "Insulated stainless steel bottle keeps drinks cold for 24 hours.", "price": 499.0, "category": "Sports", "image_url": "/assets/15.jpg", "is_featured": 0, "stock_quantity": 150},
        {"title": "Office Chair", "description": "Ergonomic mesh chair with lumbar support and adjustable height.", "price": 4999.0, "category": "Furniture", "image_url": "/assets/16.jpg", "is_featured": 1, "stock_quantity": 20},
        {"title": "Desk Lamp", "description": "LED desk lamp with adjustable brightness and color temperature.", "price": 699.0, "category": "Furniture", "image_url": "/assets/17.jpg", "is_featured": 0, "stock_quantity": 55},
        {"title": "Wall Clock", "description": "Minimalist silent wall clock for modern interiors.", "price": 449.0, "category": "Furniture", "image_url": "/assets/18.jpg", "is_featured": 0, "stock_quantity": 70},
        {"title": "Table Lamp", "description": "Vintage-style table lamp with warm ambient lighting.", "price": 799.0, "category": "Furniture", "image_url": "/assets/19.jpg", "is_featured": 0, "stock_quantity": 45},
        {"title": "Cookware Set", "description": "Non-stick cookware set of 5 with induction compatibility.", "price": 1599.0, "category": "Appliances", "image_url": "/assets/20.jpg", "is_featured": 0, "stock_quantity": 30},
        {"title": "Gaming Console", "description": "Next-gen gaming console with 1TB storage and ray tracing.", "price": 39999.0, "category": "Gaming", "image_url": "/assets/29.jpg", "is_featured": 1, "stock_quantity": 10},
        {"title": "Gaming Chair", "description": "Racing-style gaming chair with recline and footrest.", "price": 7999.0, "category": "Gaming", "image_url": "/assets/30.jpg", "is_featured": 0, "stock_quantity": 15},
        {"title": "Smart TV", "description": "55-inch 4K smart TV with HDR and built-in streaming apps.", "price": 32999.0, "category": "Electronics", "image_url": "/assets/31.jpg", "is_featured": 1, "stock_quantity": 12},
        {"title": "Soundbar", "description": "2.1 channel soundbar with wireless subwoofer.", "price": 4999.0, "category": "Electronics", "image_url": "/assets/32.jpg", "is_featured": 0, "stock_quantity": 25},
        {"title": "Tablet", "description": "10-inch tablet with stylus support and 128GB storage.", "price": 14999.0, "category": "Electronics", "image_url": "/assets/33.jpg", "is_featured": 0, "stock_quantity": 18},
        {"title": "Robot Vacuum", "description": "Smart robot vacuum with app control and auto-charge.", "price": 9999.0, "category": "Appliances", "image_url": "/assets/34.jpg", "is_featured": 1, "stock_quantity": 14},
        {"title": "Air Fryer", "description": "Digital air fryer with 5L capacity and preset menus.", "price": 3499.0, "category": "Appliances", "image_url": "/assets/35.jpg", "is_featured": 0, "stock_quantity": 28},
        {"title": "Blender", "description": "High-speed blender for smoothies, soups, and shakes.", "price": 1999.0, "category": "Appliances", "image_url": "/assets/36.jpg", "is_featured": 0, "stock_quantity": 40},
        {"title": "Microwave Oven", "description": "20L solo microwave with defrost and timer functions.", "price": 4499.0, "category": "Appliances", "image_url": "/assets/37.jpg", "is_featured": 0, "stock_quantity": 22},
        {"title": "Leather Wallet", "description": "Genuine leather bifold wallet with RFID blocking.", "price": 699.0, "category": "Fashion", "image_url": "/assets/1.jpg", "is_featured": 0, "stock_quantity": 100},
        {"title": "Wristwatch", "description": "Classic analog wristwatch with genuine leather strap.", "price": 1299.0, "category": "Fashion", "image_url": "/assets/2.jpg", "is_featured": 0, "stock_quantity": 60},
        {"title": "T-Shirt", "description": "Premium cotton round-neck t-shirt in multiple colors.", "price": 499.0, "category": "Fashion", "image_url": "/assets/3.jpg", "is_featured": 0, "stock_quantity": 200},
        {"title": "Jeans", "description": "Slim-fit stretch denim jeans for everyday comfort.", "price": 1199.0, "category": "Fashion", "image_url": "/assets/4.jpg", "is_featured": 0, "stock_quantity": 80},
        {"title": "Skincare Kit", "description": "Complete skincare routine kit with cleanser, toner, and moisturizer.", "price": 899.0, "category": "Beauty", "image_url": "/assets/5.jpg", "is_featured": 0, "stock_quantity": 55},
        {"title": "Perfume", "description": "Long-lasting Eau de Parfum with floral and woody notes.", "price": 1599.0, "category": "Beauty", "image_url": "/assets/7.png", "is_featured": 0, "stock_quantity": 45},
        {"title": "Hair Dryer", "description": "Ionic hair dryer with multiple heat and speed settings.", "price": 999.0, "category": "Beauty", "image_url": "/assets/8.jpg", "is_featured": 0, "stock_quantity": 65},
        {"title": "Tennis Racket", "description": "Lightweight graphite tennis racket for intermediate players.", "price": 1899.0, "category": "Sports", "image_url": "/assets/9.jpg", "is_featured": 0, "stock_quantity": 30},
        {"title": "Football", "description": "FIFA-approved size 5 football with butyl bladder.", "price": 699.0, "category": "Sports", "image_url": "/assets/10.jpg", "is_featured": 0, "stock_quantity": 90},
        {"title": "Dumbbell Set", "description": "Adjustable dumbbell set from 2kg to 20kg with carry case.", "price": 2499.0, "category": "Sports", "image_url": "/assets/11.jpg", "is_featured": 0, "stock_quantity": 25},
        {"title": "Tent", "description": "3-person waterproof camping tent with easy setup.", "price": 2999.0, "category": "Sports", "image_url": "/assets/12.jpg", "is_featured": 0, "stock_quantity": 18},
        {"title": "Cookbook", "description": "500 easy recipes for beginners with step-by-step photos.", "price": 599.0, "category": "Books", "image_url": "/assets/13.jpg", "is_featured": 0, "stock_quantity": 70},
        {"title": "Self-Help Book", "description": "Transform your mindset and achieve your goals.", "price": 349.0, "category": "Books", "image_url": "/assets/14.jpg", "is_featured": 0, "stock_quantity": 85},
        {"title": "Children's Storybook", "description": "Illustrated stories that spark imagination in young minds.", "price": 249.0, "category": "Books", "image_url": "/assets/15.jpg", "is_featured": 0, "stock_quantity": 110},
        {"title": "Board Game", "description": "Family strategy board game for 2-6 players aged 8+.", "price": 799.0, "category": "Gaming", "image_url": "/assets/16.jpg", "is_featured": 0, "stock_quantity": 40},
        {"title": "Puzzle Set", "description": "1000-piece jigsaw puzzle featuring a beautiful landscape.", "price": 399.0, "category": "Gaming", "image_url": "/assets/17.jpg", "is_featured": 0, "stock_quantity": 60},
        {"title": "Electric Toothbrush", "description": "Sonic electric toothbrush with 5 cleaning modes and timer.", "price": 1299.0, "category": "Beauty", "image_url": "/assets/18.jpg", "is_featured": 0, "stock_quantity": 50},
        {"title": "Face Mask Pack", "description": "Pack of 10 hydrating sheet masks for glowing skin.", "price": 299.0, "category": "Beauty", "image_url": "/assets/19.jpg", "is_featured": 0, "stock_quantity": 120},
        {"title": "Throw Pillow", "description": "Soft decorative throw pillow cover with modern geometric print.", "price": 349.0, "category": "Furniture", "image_url": "/assets/20.jpg", "is_featured": 0, "stock_quantity": 80},
    ]

    try:
        for product_data in products:
            existing = db.query(Product).filter(Product.title == product_data["title"]).first()
            if not existing:
                product = ProductCreate(**product_data)
                create_product(db, product)
                print(f"Added: {product_data['title']}")
            else:
                print(f"Already exists: {product_data['title']}")
        print("\nSeeding completed! 50 products added.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
    seed_products()

