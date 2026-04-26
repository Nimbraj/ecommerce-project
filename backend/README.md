# ShopSwift FastAPI Backend

## Setup & Run

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Seed Database (first time only)
```bash
python seed.py
```

### 3. Start Server
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /api/register | Register new user | No |
| POST | /api/login | Login & get JWT token | No |
| GET | /api/me | Get current user | Yes |
| GET | /api/products | Get all products | No |
| GET | /api/products/{id} | Get product by ID | No |
| POST | /api/products | Add new product | Yes |
| DELETE | /api/products/{id} | Delete product | Yes |
| GET | /api/cart | Get cart items | Yes |
| POST | /api/cart | Add to cart | Yes |
| PUT | /api/cart/{id} | Update cart quantity | Yes |
| DELETE | /api/cart/{id} | Remove cart item | Yes |
| DELETE | /api/cart | Clear entire cart | Yes |

## Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

