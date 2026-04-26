"""Seed script compatible with main.py schema (shopswift.db)"""
import sys
sys.path.insert(0, 'c:/Users/Admin/Desktop/Ecommerc/backend')

from main import Base, engine, SessionLocal, User, Product, get_password_hash
from datetime import datetime, timedelta

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed admin
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                name="Demo Admin",
                email="admin@example.com",
                hashed_password=get_password_hash("Admin@123"),
                is_admin=True,
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("Added admin: admin@example.com / Admin@123")
        else:
            print("Admin already exists")

        # Seed regular user
        user = db.query(User).filter(User.email == "user@example.com").first()
        if not user:
            user = User(
                name="Demo User",
                email="user@example.com",
                hashed_password=get_password_hash("User@123"),
                is_admin=False,
                role="user"
            )
            db.add(user)
            db.commit()
            print("Added user: user@example.com / User@123")
        else:
            print("User already exists")

        # Seed products
        products = [
            {"title": "Wireless Headphones", "description": "Premium wireless headphones with noise cancellation and 20-hour battery life.", "price": 3999.0, "category": "Electronics", "image_url": "/assets/21.jpg", "stock_quantity": 45, "low_stock_threshold": 5},
            {"title": "Smart Watch", "description": "Stay connected and track your health with this advanced smart watch.", "price": 2999.0, "category": "Electronics", "image_url": "/assets/22.jpg", "stock_quantity": 30, "low_stock_threshold": 5},
            {"title": "Bluetooth Speaker", "description": "Compact and waterproof speaker with deep bass and long battery life.", "price": 1499.0, "category": "Electronics", "image_url": "/assets/23.jpg", "stock_quantity": 60, "low_stock_threshold": 5},
            {"title": "DSLR Camera", "description": "Professional-quality DSLR camera for stunning photography and video.", "price": 25999.0, "category": "Electronics", "image_url": "/assets/24.jpg", "stock_quantity": 12, "low_stock_threshold": 3},
            {"title": "Gaming Mouse", "description": "High-precision gaming mouse with customizable buttons and RGB lighting.", "price": 999.0, "category": "Gaming", "image_url": "/assets/25.jpg", "stock_quantity": 80, "low_stock_threshold": 10},
            {"title": "Mechanical Keyboard", "description": "Durable mechanical keyboard with tactile feedback and backlit keys.", "price": 2199.0, "category": "Gaming", "image_url": "/assets/26.jpg", "stock_quantity": 55, "low_stock_threshold": 5},
            {"title": "4K Monitor", "description": "Ultra HD 4K monitor with vibrant colors and sharp display for professionals.", "price": 19999.0, "category": "Electronics", "image_url": "/assets/27.jpg", "stock_quantity": 18, "low_stock_threshold": 3},
            {"title": "Noise Cancelling Earbuds", "description": "Compact earbuds with active noise cancelling and long battery life.", "price": 1799.0, "category": "Electronics", "image_url": "/assets/28.jpg", "stock_quantity": 70, "low_stock_threshold": 5},
            {"title": "Portable Charger", "description": "High-capacity 20000mAh power bank with fast charging support.", "price": 1299.0, "category": "Electronics", "image_url": "/assets/1.jpg", "stock_quantity": 100, "low_stock_threshold": 10},
            {"title": "Fitness Tracker", "description": "Lightweight fitness band with heart rate monitor and sleep tracking.", "price": 1499.0, "category": "Electronics", "image_url": "/assets/2.jpg", "stock_quantity": 65, "low_stock_threshold": 5},
            {"title": "Drone with Camera", "description": "Easy-to-fly drone with 4K camera and GPS stabilization.", "price": 8999.0, "category": "Electronics", "image_url": "/assets/3.jpg", "stock_quantity": 15, "low_stock_threshold": 3},
            {"title": "VR Headset", "description": "Immersive virtual reality headset for gaming and media.", "price": 4999.0, "category": "Gaming", "image_url": "/assets/4.jpg", "stock_quantity": 22, "low_stock_threshold": 5},
            {"title": "Action Camera", "description": "Rugged waterproof action camera for adventure sports.", "price": 6999.0, "category": "Electronics", "image_url": "/assets/5.jpg", "stock_quantity": 28, "low_stock_threshold": 5},
            {"title": "Smart Home Hub", "description": "Control all your smart devices from one central hub.", "price": 3499.0, "category": "Electronics", "image_url": "/assets/7.png", "stock_quantity": 40, "low_stock_threshold": 5},
            {"title": "Wireless Earphones", "description": "True wireless earphones with deep bass and touch controls.", "price": 899.0, "category": "Electronics", "image_url": "/assets/8.jpg", "stock_quantity": 90, "low_stock_threshold": 10},
            {"title": "Bestselling Novel", "description": "A gripping storyline that keeps you hooked till the last page.", "price": 399.0, "category": "Books", "image_url": "/assets/9.jpg", "stock_quantity": 120, "low_stock_threshold": 10},
            {"title": "Coffee Maker", "description": "Brew barista-quality coffee at home with this compact machine.", "price": 2499.0, "category": "Appliances", "image_url": "/assets/10.jpg", "stock_quantity": 35, "low_stock_threshold": 5},
            {"title": "Running Shoes", "description": "Lightweight cushioned running shoes for daily workouts.", "price": 1999.0, "category": "Fashion", "image_url": "/assets/11.jpg", "stock_quantity": 50, "low_stock_threshold": 5},
            {"title": "Yoga Mat", "description": "Non-slip eco-friendly yoga mat with carrying strap.", "price": 599.0, "category": "Sports", "image_url": "/assets/12.jpg", "stock_quantity": 75, "low_stock_threshold": 10},
            {"title": "Backpack", "description": "Durable water-resistant backpack with laptop compartment.", "price": 1299.0, "category": "Fashion", "image_url": "/assets/13.jpg", "stock_quantity": 60, "low_stock_threshold": 5},
            {"title": "Sunglasses", "description": "UV-protected polarized sunglasses with premium frames.", "price": 899.0, "category": "Fashion", "image_url": "/assets/14.jpg", "stock_quantity": 85, "low_stock_threshold": 10},
            {"title": "Water Bottle", "description": "Insulated stainless steel bottle keeps drinks cold for 24 hours.", "price": 499.0, "category": "Sports", "image_url": "/assets/15.jpg", "stock_quantity": 150, "low_stock_threshold": 15},
            {"title": "Office Chair", "description": "Ergonomic mesh chair with lumbar support and adjustable height.", "price": 4999.0, "category": "Furniture", "image_url": "/assets/16.jpg", "stock_quantity": 20, "low_stock_threshold": 3},
            {"title": "Desk Lamp", "description": "LED desk lamp with adjustable brightness and color temperature.", "price": 699.0, "category": "Furniture", "image_url": "/assets/17.jpg", "stock_quantity": 55, "low_stock_threshold": 5},
            {"title": "Wall Clock", "description": "Minimalist silent wall clock for modern interiors.", "price": 449.0, "category": "Furniture", "image_url": "/assets/18.jpg", "stock_quantity": 70, "low_stock_threshold": 10},
            {"title": "Table Lamp", "description": "Vintage-style table lamp with warm ambient lighting.", "price": 799.0, "category": "Furniture", "image_url": "/assets/19.jpg", "stock_quantity": 45, "low_stock_threshold": 5},
            {"title": "Cookware Set", "description": "Non-stick cookware set of 5 with induction compatibility.", "price": 1599.0, "category": "Appliances", "image_url": "/assets/20.jpg", "stock_quantity": 30, "low_stock_threshold": 5},
            {"title": "Gaming Console", "description": "Next-gen gaming console with 1TB storage and ray tracing.", "price": 39999.0, "category": "Gaming", "image_url": "/assets/29.jpg", "stock_quantity": 10, "low_stock_threshold": 2},
            {"title": "Gaming Chair", "description": "Racing-style gaming chair with recline and footrest.", "price": 7999.0, "category": "Gaming", "image_url": "/assets/30.jpg", "stock_quantity": 15, "low_stock_threshold": 3},
            {"title": "Smart TV", "description": "55-inch 4K smart TV with HDR and built-in streaming apps.", "price": 32999.0, "category": "Electronics", "image_url": "/assets/31.jpg", "stock_quantity": 12, "low_stock_threshold": 3},
            {"title": "Soundbar", "description": "2.1 channel soundbar with wireless subwoofer.", "price": 4999.0, "category": "Electronics", "image_url": "/assets/32.jpg", "stock_quantity": 25, "low_stock_threshold": 5},
            {"title": "Tablet", "description": "10-inch tablet with stylus support and 128GB storage.", "price": 14999.0, "category": "Electronics", "image_url": "/assets/33.jpg", "stock_quantity": 18, "low_stock_threshold": 3},
            {"title": "Robot Vacuum", "description": "Smart robot vacuum with app control and auto-charge.", "price": 9999.0, "category": "Appliances", "image_url": "/assets/34.jpg", "stock_quantity": 14, "low_stock_threshold": 3},
            {"title": "Air Fryer", "description": "Digital air fryer with 5L capacity and preset menus.", "price": 3499.0, "category": "Appliances", "image_url": "/assets/35.jpg", "stock_quantity": 28, "low_stock_threshold": 5},
            {"title": "Blender", "description": "High-speed blender for smoothies, soups, and shakes.", "price": 1999.0, "category": "Appliances", "image_url": "/assets/36.jpg", "stock_quantity": 40, "low_stock_threshold": 5},
            {"title": "Microwave Oven", "description": "20L solo microwave with defrost and timer functions.", "price": 4499.0, "category": "Appliances", "image_url": "/assets/37.jpg", "stock_quantity": 22, "low_stock_threshold": 5},
            {"title": "Leather Wallet", "description": "Genuine leather bifold wallet with RFID blocking.", "price": 699.0, "category": "Fashion", "image_url": "/assets/1.jpg", "stock_quantity": 100, "low_stock_threshold": 10},
            {"title": "Wristwatch", "description": "Classic analog wristwatch with genuine leather strap.", "price": 1299.0, "category": "Fashion", "image_url": "/assets/2.jpg", "stock_quantity": 60, "low_stock_threshold": 5},
            {"title": "T-Shirt", "description": "Premium cotton round-neck t-shirt in multiple colors.", "price": 499.0, "category": "Fashion", "image_url": "/assets/3.jpg", "stock_quantity": 200, "low_stock_threshold": 20},
            {"title": "Jeans", "description": "Slim-fit stretch denim jeans for everyday comfort.", "price": 1199.0, "category": "Fashion", "image_url": "/assets/4.jpg", "stock_quantity": 80, "low_stock_threshold": 10},
            {"title": "Skincare Kit", "description": "Complete skincare routine kit with cleanser, toner, and moisturizer.", "price": 899.0, "category": "Beauty", "image_url": "/assets/5.jpg", "stock_quantity": 55, "low_stock_threshold": 5},
            {"title": "Perfume", "description": "Long-lasting Eau de Parfum with floral and woody notes.", "price": 1599.0, "category": "Beauty", "image_url": "/assets/7.png", "stock_quantity": 45, "low_stock_threshold": 5},
            {"title": "Hair Dryer", "description": "Ionic hair dryer with multiple heat and speed settings.", "price": 999.0, "category": "Beauty", "image_url": "/assets/8.jpg", "stock_quantity": 65, "low_stock_threshold": 5},
            {"title": "Tennis Racket", "description": "Lightweight graphite tennis racket for intermediate players.", "price": 1899.0, "category": "Sports", "image_url": "/assets/9.jpg", "stock_quantity": 30, "low_stock_threshold": 5},
            {"title": "Football", "description": "FIFA-approved size 5 football with butyl bladder.", "price": 699.0, "category": "Sports", "image_url": "/assets/10.jpg", "stock_quantity": 90, "low_stock_threshold": 10},
            {"title": "Dumbbell Set", "description": "Adjustable dumbbell set from 2kg to 20kg with carry case.", "price": 2499.0, "category": "Sports", "image_url": "/assets/11.jpg", "stock_quantity": 25, "low_stock_threshold": 3},
            {"title": "Tent", "description": "3-person waterproof camping tent with easy setup.", "price": 2999.0, "category": "Sports", "image_url": "/assets/12.jpg", "stock_quantity": 18, "low_stock_threshold": 3},
            {"title": "Cookbook", "description": "500 easy recipes for beginners with step-by-step photos.", "price": 599.0, "category": "Books", "image_url": "/assets/13.jpg", "stock_quantity": 70, "low_stock_threshold": 5},
            {"title": "Self-Help Book", "description": "Transform your mindset and achieve your goals.", "price": 349.0, "category": "Books", "image_url": "/assets/14.jpg", "stock_quantity": 85, "low_stock_threshold": 10},
            {"title": "Children's Storybook", "description": "Illustrated stories that spark imagination in young minds.", "price": 249.0, "category": "Books", "image_url": "/assets/15.jpg", "stock_quantity": 110, "low_stock_threshold": 10},
            {"title": "Board Game", "description": "Family strategy board game for 2-6 players aged 8+.", "price": 799.0, "category": "Gaming", "image_url": "/assets/16.jpg", "stock_quantity": 40, "low_stock_threshold": 5},
            {"title": "Puzzle Set", "description": "1000-piece jigsaw puzzle featuring a beautiful landscape.", "price": 399.0, "category": "Gaming", "image_url": "/assets/17.jpg", "stock_quantity": 60, "low_stock_threshold": 5},
            {"title": "Electric Toothbrush", "description": "Sonic electric toothbrush with 5 cleaning modes and timer.", "price": 1299.0, "category": "Beauty", "image_url": "/assets/18.jpg", "stock_quantity": 50, "low_stock_threshold": 5},
            {"title": "Face Mask Pack", "description": "Pack of 10 hydrating sheet masks for glowing skin.", "price": 299.0, "category": "Beauty", "image_url": "/assets/19.jpg", "stock_quantity": 120, "low_stock_threshold": 10},
            {"title": "Throw Pillow", "description": "Soft decorative throw pillow cover with modern geometric print.", "price": 349.0, "category": "Furniture", "image_url": "/assets/20.jpg", "stock_quantity": 80, "low_stock_threshold": 10},
        ]

        for p in products:
            existing = db.query(Product).filter(Product.title == p["title"]).first()
            if not existing:
                db.add(Product(**p))
                print(f"Added: {p['title']}")
            else:
                print(f"Already exists: {p['title']}")
        db.commit()
        print(f"\nSeeding completed! {len(products)} products added.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()

