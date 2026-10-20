# JN ECOMMERCE FastAPI Backend

## Setup & Run

### 1. Install Dependencies
```bash
cd backend
python -m pip install -r ../requirements.txt
```

### 2. Seed Database (first time only)
```bash
python seed_main.py
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

## Deploying to Render

The repository includes a `render.yaml` Blueprint for a FastAPI service and a
persistent PostgreSQL database. In Render, create a new Blueprint from this
repository and provide `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD`
when prompted. The service seeds the catalog on startup and creates the initial
administrator if that email is not already present.

The Render database starts empty; it does not import the local SQLite database.
Back up and migrate any local data separately if it needs to be retained.

After the API is deployed:

1. Set `CORS_ORIGINS` on the Render service to `https://nimbraj.github.io`.
2. Copy the service's public URL (without `/api`) into the GitHub repository
   Actions variable `VITE_API_URL` under **Settings → Secrets and variables →
   Actions → Variables**.
3. Rerun the GitHub Pages deployment workflow.

The Pages workflow now fails instead of publishing a frontend build that would
fall back to `localhost` when `VITE_API_URL` is missing.
