# Admin Panel Implementation TODO

## Phase 1: Backend — Database Models & Schemas
- [ ] Update `backend/models.py` — Add sku/status to Product, role/is_banned to User, Category, TaxRule, AuditLog models
- [ ] Update `backend/schemas.py` — Add new enums and schemas for ProductStatus, UserRole, Category, TaxRule, AuditLog, AdminUserCreate, DraftOrderCreate

## Phase 2: Backend — CRUD Layer
- [ ] Update `backend/crud.py` — Add audit logging helper, Category CRUD, TaxRule CRUD, Admin User CRUD, Draft Order/Cancel/Refund, wrap updates/deletes with audit logs

## Phase 3: Backend — API Endpoints & Auth
- [ ] Update `backend/auth.py` — Add get_current_manager_user() for admin/manager roles
- [ ] Update `backend/main.py` — Add admin product filters, draft order, cancel/refund, user CRUD, category CRUD, tax rule CRUD, audit log endpoint

## Phase 4: Frontend — API Service
- [ ] Update `ecommerc-app/src/services/api.js` — Add all new admin API functions

## Phase 5: Frontend — Admin Dashboard UI
- [ ] Update `ecommerc-app/src/Component/AdminDashboard.jsx` — Add Products, Customers, Categories, Tax Rules, Audit Logs tabs with full CRUD UI

## Phase 6: Validation & Testing
- [ ] Run backend, verify tables created
- [ ] Smoke test all new admin features

