import os

path = r'c:\Users\Admin\Desktop\Ecommerc\ecommerc-app\src\Component\AdminDashboard.jsx'
f = open(path, 'w', encoding='utf-8')

# --- PART 1: Imports and setup ---
f.write("""import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";
import {
  getAdminAnalytics, getAllOrders, updateOrderStatus, getLowStock, updateInventory,
  getCoupons, createCoupon, deleteCoupon, getAdminProducts, createProduct, updateProduct, deleteProduct,
  getUsers, createUserAdmin, updateUserAdmin, deleteUserAdmin, banUser, unbanUser,
  getCategories, createCategory, updateCategory, deleteCategory,
  getTaxRules, createTaxRule, updateTaxRule, deleteTaxRule,
  getAuditLogs, createDraftOrder, cancelOrder, refundOrder,
} from "../services/api";

const COLORS = ["#0d9488", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"];
const STATUS_OPTIONS = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"];
const PRODUCT_STATUS_OPTIONS = ["active", "draft", "archived", "out_of_stock"];
const ROLE_OPTIONS = ["customer", "manager", "admin"];

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [tab, setTab] = useState("analytics");
  const [analytics, setAnalytics] = useState(null);
  const [orders, setOrders] = useState([]);
  const [lowStock, setLowStock] = useState([]);
  const [products, setProducts] = useState([]);
  const [coupons, setCoupons] = useState([]);
  const [users, setUsers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [taxRules, setTaxRules] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [productFilter, setProductFilter] = useState({ category: "", status: "" });
  const [userSearch, setUserSearch] = useState("");

  const [productModal, setProductModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [userModal, setUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [categoryModal, setCategoryModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [taxModal, setTaxModal] = useState(false);
  const [editingTax, setEditingTax] = useState(null);
  const [draftOrderModal, setDraftOrderModal] = useState(false);

  const [productForm, setProductForm] = useState({ title: "", sku: "", slug: "", description: "", price: "", category: "", image_url: "", status: "active", stock_quantity: "100", low_stock_threshold: "10", is_featured: 0 });
  const [couponForm, setCouponForm] = useState({ code: "", coupon_type: "percentage", value: "", min_order_value: "", max_discount: "", usage_limit: "", valid_until: "" });
  const [userForm, setUserForm] = useState({ name: "", email: "", password: "", address: "", mobile: "", role: "customer" });
  const [categoryForm, setCategoryForm] = useState({ name: "", slug: "", description: "", parent_id: "" });
  const [taxForm, setTaxForm] = useState({ name: "", rate: "", country: "", region: "", is_active: 1 });
  const [draftOrderForm, setDraftOrderForm] = useState({ items: [{ product_id: "", quantity: "", unit_price: "" }], guest_email: "", guest_name: "", guest_mobile: "", guest_address: "", payment_method: "card" });
  const [inventoryEdits, setInventoryEdits] = useState({});

  useEffect(() => { fetchAll(); }, []);
  const fetchAll = async () => {
    setLoading(true); setError("");
    try {
      const [a, o, l, p, c] = await Promise.all([getAdminAnalytics(), getAllOrders(), getLowStock(), getAdminProducts(), getCoupons()]);
      setAnalytics(a); setOrders(o); setLowStock(l); setProducts(p); setCoupons(c);
    } catch (err) { setError(err.message || "Failed"); if (err.message?.includes("Admin")) navigate("/"); }
    finally { setLoading(false); }
  };
  const fetchTabData = async (tabName) => {
    try {
      if (tabName === "customers") { const u = await getUsers(userSearch); setUsers(u); }
      else if (tabName === "categories") { const cats = await getCategories(); setCategories(cats); }
      else if (tabName === "taxes") { const t = await getTaxRules(); setTaxRules(t); }
      else if (tabName === "audit") { const logs = await getAuditLogs(); setAuditLogs(logs); }
      else if (tabName === "products") { const p = await getAdminProducts(productFilter.category || undefined, productFilter.status || undefined); setProducts(p); }
    } catch (err) { alert(err.message); }
  };
  useEffect(() => { if (["customers","categories","taxes","audit","products"].includes(tab)) fetchTabData(tab); }, [tab]);

  const handleStatusChange = async (orderId, newStatus) => { try { await updateOrderStatus(orderId, newStatus); setOrders((prev) => prev.map((o) => (o.id === orderId ? { ...o, status: newStatus } : o))); } catch (err) { alert(err.message); } };
  const handleInventoryUpdate = async (productId, newStock, threshold) => { try { await updateInventory(productId, Number(newStock), Number(threshold)); setProducts((prev) => prev.map((p) => (p.id === productId ? { ...p, stock_quantity: Number(newStock), low_stock_threshold: Number(threshold) } : p))); const l = await getLowStock(); setLowStock(l); alert("Inventory updated"); } catch (err) { alert(err.message); } };
  const handleCreateCoupon = async (e) => { e.preventDefault(); try { const payload = { ...couponForm, value: Number(couponForm.value), min_order_value: Number(couponForm.min_order_value || 0), max_discount: couponForm.max_discount ? Number(couponForm.max_discount) : null, usage_limit: Number(couponForm.usage_limit || 1), valid_until: couponForm.valid_until ? new Date(couponForm.valid_until).toISOString() : null }; await createCoupon(payload); setCouponForm({ code: "", coupon_type: "percentage", value: "", min_order_value: "", max_discount: "", usage_limit: "", valid_until: "" }); const c = await getCoupons(); setCoupons(c); alert("Coupon created!"); } catch (err) { alert(err.message); } };
  const handleDeleteCoupon = async (id) => { if (!window.confirm("Delete?")) return; try { await deleteCoupon(id); setCoupons((prev) => prev.filter((c) => c.id !== id)); } catch (err) { alert(err.message); } };

  const openProductModal = (product = null) => { if (product) { setEditingProduct(product); setProductForm({ title: product.title || "", sku: product.sku || "", slug: product.slug || "", description: product.description || "", price: product.price || "", category: product.category || "", image_url: product.image_url || "", status: product.status || "active", stock_quantity: product.stock_quantity || "100", low_stock_threshold: product.low_stock_threshold || "10", is_featured: product.is_featured || 0 }); } else { setEditingProduct(null); setProductForm({ title: "", sku: "", slug: "", description: "", price: "", category: "", image_url: "", status: "active", stock_quantity: "100", low_stock_threshold: "10", is_featured: 0 }); } setProductModal(true); };
  const handleProductSave = async (e) => { e.preventDefault(); try { const payload = { ...productForm, price: Number(productForm.price), stock_quantity: Number(productForm.stock_quantity), low_stock_threshold: Number(productForm.low_stock_threshold), is_featured: Number(productForm.is_featured) }; if (editingProduct) { await updateProduct(editingProduct.id, payload); } else { await createProduct(payload); } setProductModal(false); const p = await getAdminProducts(productFilter.category || undefined, productFilter.status || undefined); setProducts(p); } catch (err) { alert(err.message); } };
  const handleDeleteProduct = async (id) => { if (!window.confirm("Delete?")) return; try { await deleteProduct(id); setProducts((prev) => prev.filter((p) => p.id !== id)); } catch (err) { alert(err.message); } };

  const openUserModal = (user = null) => { if (user) { setEditingUser(user); setUserForm({ name: user.name || "", email: user.email || "", password: "", address: user.address || "", mobile: user.mobile || "", role: user.role || "customer" }); } else { setEditingUser(null); setUserForm({ name: "", email: "", password: "", address: "", mobile: "", role: "customer" }); } setUserModal(true); };
  const handleUserSave = async (e) => { e.preventDefault(); try { if (editingUser) { const payload = { ...userForm }; if (!payload.password) delete payload.password; await updateUserAdmin(editingUser.id, payload); } else { await createUserAdmin(userForm); } setUserModal(false); const u = await getUsers(userSearch); setUsers(u); } catch (err) { alert(err.message); } };
  const handleDeleteUser = async (id) => { if (!window.confirm("Delete?")) return; try { await deleteUserAdmin(id); setUsers((prev) => prev.filter((u) => u.id !== id)); } catch (err) { alert(err.message); } };
  const handleBanUserToggle = async (id, ban) => { try { if (ban) await banUser(id); else await unbanUser(id); const u = await getUsers(userSearch); setUsers(u); } catch (err) { alert(err.message); } };

  const openCategoryModal = (cat = null) => { if (cat) { setEditingCategory(cat); setCategoryForm({ name: cat.name || "", slug: cat.slug || "", description: cat.description || "", parent_id: cat.parent_id || "" }); } else { setEditingCategory(null); setCategoryForm({ name: "", slug: "", description: "", parent_id: "" }); } setCategoryModal(true); };
  const handleCategorySave = async (e) => { e.preventDefault(); try { const payload = { ...categoryForm }; if (!payload.parent_id) delete payload.parent_id; if (editingCategory) { await updateCategory(editingCategory.id, payload); } else { await createCategory(payload); } setCategoryModal(false); const cats = await getCategories(); setCategories(cats); } catch (err) { alert(err.message); } };
  const handleDeleteCategory = async (id) => { if (!window.confirm("Delete?")) return; try { await deleteCategory(id); setCategories((prev) => prev.filter((c) => c.id !== id)); } catch (err) { alert(err.message); } };

  const openTaxModal = (tax = null) => { if (tax) { setEditingTax(tax); setTaxForm({ name: tax.name || "", rate: tax.rate || "", country: tax.country || "", region: tax.region || "", is_active: tax.is_active ?? 1 }); } else { setEditingTax(null); setTaxForm({ name: "", rate: "", country: "", region: "", is_active: 1 }); } setTaxModal(true); };
  const handleTaxSave = async (e) => { e.preventDefault(); try { const payload = { ...taxForm, rate: Number(taxForm.rate), is_active: Number(taxForm.is_active) }; if (editingTax) { await updateTaxRule(editingTax.id, payload); } else { await createTaxRule(payload); } setTaxModal(false); const t = await getTaxRules(); setTaxRules(t); } catch (err) { alert(err.message); } };
  const handleDeleteTax = async (id) => { if (!window.confirm("Delete?")) return; try { await deleteTaxRule(id); setTaxRules((prev) => prev.filter((t) => t.id !== id)); } catch (err) { alert(err.message); } };

  const handleDraftOrderSave = async (e) => { e.preventDefault(); try { const payload = { ...draftOrderForm, items: draftOrderForm.items.map((item) => ({ product_id: Number(item.product_id), quantity: Number(item.quantity), unit_price: Number(item.unit_price) })) }; await createDraftOrder(payload); setDraftOrderModal(false); setDraftOrderForm({ items: [{ product_id: "", quantity: "", unit_price: "" }], guest_email: "", guest_name: "", guest_mobile: "", guest_address: "", payment_method: "card" }); const o = await getAllOrders(); setOrders(o); alert("Draft order created!"); } catch (err) { alert(err.message); } };
  const handleCancelOrder = async (orderId) => { if (!window.confirm("Cancel?")) return; try { await cancelOrder(orderId); const o = await getAllOrders(); setOrders(o); } catch (err) { alert(err.message); } };
  const handleRefundOrder = async (orderId) => { if (!window.confirm("Refund?")) return; try { await refundOrder(orderId); const o = await getAllOrders(); setOrders(o); } catch (err) { alert(err.message); } };

  if (loading) return <div className="pt-24 text-center">Loading...</div>;
  if (error) return <div className="pt-24 text-center text-red-500">{error}</div>;

  const summary = analytics?.sales_summary || {};
  const topProducts = analytics?.top_products || [];
  const recentOrders = analytics?.recent_orders || [];

  const tabs = [
    { id: "analytics", label: "Analytics" },
    { id: "orders", label: "Orders" },
    { id: "products", label: "Products" },
    { id: "inventory", label: "Inventory" },
    { id: "coupons", label: "Coupons" },
    { id: "customers", label: "Customers" },
    { id: "categories", label: "Categories" },
    { id: "taxes", label: "Tax Rules" },
    { id: "drafts", label: "Draft Orders" },
    { id: "audit", label: "Audit Logs" }
  ];

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="mt-1 text-sm text-gray-500">Manage your store efficiently</p>
          </div>
          <button
            onClick={() => navigate("/")}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Back to Store
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm mb-6">
          <nav className="flex flex-wrap gap-1 p-2">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  tab === t.id
                    ? "bg-teal-600 text-white"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                {t.label}
              </button>
            ))}
          </nav>
        </div>

        <motion.div
          key={tab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
""")

# --- PART 2: Analytics Tab ---
f.write("""
          {tab === "analytics" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <p className="text-sm font-medium text-gray-600">Total Orders</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{summary.total_orders || 0}</p>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <p className="text-sm font-medium text-gray-600">Today's Orders</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{summary.today_orders || 0}</p>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <p className="text-sm font-medium text-gray-600">Total Revenue</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">${(summary.total_revenue || 0).toFixed(2)}</p>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <p className="text-sm font-medium text-gray-600">Today's Revenue</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">${(summary.today_revenue || 0).toFixed(2)}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4">Top Products</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={topProducts}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="title" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="total_sold" fill="#0d9488" name="Units Sold" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4">Revenue by Product</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={topProducts}
                        dataKey="total_revenue"
                        nameKey="title"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label
                      >
                        {topProducts.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Recent Orders</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Order ID</th>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Status</th>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Total</th>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Items</th>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentOrders.map((order) => (
                        <tr key={order.id} className="border-b">
                          <td className="px-4 py-3 text-sm">#{order.id}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              order.status === "delivered" ? "bg-green-100 text-green-800" :
                              order.status === "cancelled" ? "bg-red-100 text-red-800" :
                              order.status === "shipped" ? "bg-blue-100 text-blue-800" :
                              "bg-yellow-100 text-yellow-800"
                            }`}>
                              {order.status}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm">${order.total.toFixed(2)}</td>
                          <td className="px-4 py-3 text-sm">{order.item_count}</td>
                          <td className="px-4 py-3 text-sm">{new Date(order.created_at).toLocaleDateString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
""")

# --- PART 3: Orders Tab ---
f.write("""
          {tab === "orders" && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">All Orders</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">ID</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Customer</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Status</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Total</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Date</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map((order) => (
                      <tr key={order.id} className="border-b">
                        <td className="px-4 py-3 text-sm">#{order.id}</td>
                        <td className="px-4 py-3 text-sm">{order.user?.name || "N/A"}</td>
                        <td className="px-4 py-3">
                          <select
                            value={order.status}
                            onChange={(e) => handleStatusChange(order.id, e.target.value)}
                            className="text-xs border rounded px-2 py-1"
                          >
                            {STATUS_OPTIONS.map((s) => (
                              <option key={s} value={s}>{s}</option>
                            ))}
                          </select>
                        </td>
                        <td className="px-4 py-3 text-sm">${order.total.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm">{new Date(order.created_at).toLocaleDateString()}</td>
                        <td className="px-4 py-3 text-sm space-x-2">
                          <button
                            onClick={() => handleCancelOrder(order.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Cancel
                          </button>
                          {order.status === "delivered" && (
                            <button
                              onClick={() => handleRefundOrder(order.id)}
                              className="text-orange-600 hover:text-orange-800"
                            >
                              Refund
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
""")

# --- PART 4: Products Tab ---
f.write("""
          {tab === "products" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex gap-4">
                  <input
                    type="text"
                    placeholder="Filter by category"
                    value={productFilter.category}
                    onChange={(e) => setProductFilter({ ...productFilter, category: e.target.value })}
                    className="border rounded px-3 py-1 text-sm"
                  />
                  <select
                    value={productFilter.status}
                    onChange={(e) => setProductFilter({ ...productFilter, status: e.target.value })}
                    className="border rounded px-3 py-1 text-sm"
                  >
                    <option value="">All Status</option>
                    {PRODUCT_STATUS_OPTIONS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => fetchTabData("products")}
                    className="bg-gray-200 px-3 py-1 rounded text-sm hover:bg-gray-300"
                  >
                    Apply Filters
                  </button>
                </div>
                <button
                  onClick={() => openProductModal()}
                  className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700"
                >
                  Add Product
                </button>
              </div>
              <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Title</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Category</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Price</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Stock</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Status</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((product) => (
                      <tr key={product.id} className="border-b">
                        <td className="px-4 py-3 text-sm font-medium">{product.title}</td>
                        <td className="px-4 py-3 text-sm">{product.category}</td>
                        <td className="px-4 py-3 text-sm">${product.price.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm">{product.stock_quantity}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            product.status === "active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                          }`}>
                            {product.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm space-x-2">
                          <button onClick={() => openProductModal(product)} className="text-teal-600 hover:text-teal-800">Edit</button>
                          <button onClick={() => handleDeleteProduct(product.id)} className="text-red-600 hover:text-red-800">Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {productModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                  <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                    <h3 className="text-lg font-semibold mb-4">{editingProduct ? "Edit Product" : "Add Product"}</h3>
                    <form onSubmit={handleProductSave} className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <input type="text" placeholder="Title" value={productForm.title} onChange={(e) => setProductForm({...productForm, title: e.target.value})} className="border rounded px-3 py-2" required />
                        <input type="text" placeholder="SKU" value={productForm.sku} onChange={(e) => setProductForm({...productForm, sku: e.target.value})} className="border rounded px-3 py-2" />
                        <input type="text" placeholder="Slug" value={productForm.slug} onChange={(e) => setProductForm({...productForm, slug: e.target.value})} className="border rounded px-3 py-2" />
                        <input type="number" placeholder="Price" value={productForm.price} onChange={(e) => setProductForm({...productForm, price: e.target.value})} className="border rounded px-3 py-2" required />
                        <input type="text" placeholder="Category" value={productForm.category} onChange={(e) => setProductForm({...productForm, category: e.target.value})} className="border rounded px-3 py-2" />
                        <input type="url" placeholder="Image URL" value={productForm.image_url} onChange={(e) => setProductForm({...productForm, image_url: e.target.value})} className="border rounded px-3 py-2" />
                        <select value={productForm.status} onChange={(e) => setProductForm({...productForm, status: e.target.value})} className="border rounded px-3 py-2">
                          {PRODUCT_STATUS_OPTIONS.map((s) => (<option key={s} value={s}>{s}</option>))}
                        </select>
                        <input type="number" placeholder="Stock" value={productForm.stock_quantity} onChange={(e) => setProductForm({...productForm, stock_quantity: e.target.value})} className="border rounded px-3 py-2" />
                        <input type="number" placeholder="Low Stock Threshold" value={productForm.low_stock_threshold} onChange={(e) => setProductForm({...productForm, low_stock_threshold: e.target.value})} className="border rounded px-3 py-2" />
                        <select value={productForm.is_featured} onChange={(e) => setProductForm({...productForm, is_featured: e.target.value})} className="border rounded px-3 py-2">
                          <option value={0}>Not Featured</option>
                          <option value={1}>Featured</option>
                        </select>
                      </div>
                      <textarea placeholder="Description" value={productForm.description} onChange={(e) => setProductForm({...productForm, description: e.target.value})} className="border rounded px-3 py-2 w-full" rows="3" />
                      <div className="flex justify-end space-x-3 pt-4">
                        <button type="button" onClick={() => setProductModal(false)} className="px-4 py-2 border rounded hover:bg-gray-50">Cancel</button>
                        <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700">Save</button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}
""")

# --- PART 5: Inventory Tab ---
f.write("""
          {tab === "inventory" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Low Stock Products</h3>
              <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Product</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Category</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Current Stock</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Threshold</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Update</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lowStock.map((product) => (
                      <tr key={product.id} className="border-b">
                        <td className="px-4 py-3 text-sm">{product.title}</td>
                        <td className="px-4 py-3 text-sm">{product.category}</td>
                        <td className="px-4 py-3 text-sm text-red-600 font-medium">{product.stock_quantity}</td>
                        <td className="px-4 py-3 text-sm">{product.low_stock_threshold}</td>
                        <td className="px-4 py-3 text-sm space-x-2">
                          <input
                            type="number"
                            placeholder="New Stock"
                            value={inventoryEdits[product.id]?.stock || ""}
                            onChange={(e) => setInventoryEdits({...inventoryEdits, [product.id]: {...inventoryEdits[product.id], stock: e.target.value}})}
                            className="border rounded px-2 py-1 w-24"
                          />
                          <input
                            type="number"
                            placeholder="Threshold"
                            value={inventoryEdits[product.id]?.threshold || ""}
                            onChange={(e) => setInventoryEdits({...inventoryEdits, [product.id]: {...inventoryEdits[product.id], threshold: e.target.value}})}
                            className="border rounded px-2 py-1 w-24"
                          />
                          <button
                            onClick={() => handleInventoryUpdate(
                              product.id,
                              inventoryEdits[product.id]?.stock || product.stock_quantity,
                              inventoryEdits[product.id]?.threshold || product.low_stock_threshold
                            )}
                            className="bg-teal-600 text-white px-3 py-1 rounded text-sm hover:bg-teal-700"
                          >
                            Update
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
""")

# --- PART 6: Coupons Tab ---
f.write("""
          {tab === "coupons" && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Create Coupon</h3>
                <form onSubmit={handleCreateCoupon} className="grid grid-cols-2 gap-4">
                  <input type="text" placeholder="Code" value={couponForm.code} onChange={(e) => setCouponForm({...couponForm, code: e.target.value})} className="border rounded px-3 py-2" required />
                  <select value={couponForm.coupon_type} onChange={(e) => setCouponForm({...couponForm, coupon_type: e.target.value})} className="border rounded px-3 py-2">
                    <option value="percentage">Percentage</option>
                    <option value="fixed">Fixed Amount</option>
                  </select>
                  <input type="number" placeholder="Value" value={couponForm.value} onChange={(e) => setCouponForm({...couponForm, value: e.target.value})} className="border rounded px-3 py-2" required />
                  <input type="number" placeholder="Min Order Value" value={couponForm.min_order_value} onChange={(e) => setCouponForm({...couponForm, min_order_value: e.target.value})} className="border rounded px-3 py-2" />
                  <input type="number" placeholder="Max Discount" value={couponForm.max_discount} onChange={(e) => setCouponForm({...couponForm, max_discount: e.target.value})} className="border rounded px-3 py-2" />
                  <input type="number" placeholder="Usage Limit" value={couponForm.usage_limit} onChange={(e) => setCouponForm({...couponForm, usage_limit: e.target.value})} className="border rounded px-3 py-2" />
                  <input type="datetime-local" placeholder="Valid Until" value={couponForm.valid_until} onChange={(e) => setCouponForm({...couponForm, valid_until: e.target.value})} className="border rounded px-3 py-2" />
                  <button type="submit" className="col-span-2 bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700">Create Coupon</button>
                </form>
              </div>
              <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Code</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Type</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Value</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Used</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Valid Until</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {coupons.map((coupon) => (
                      <tr key={coupon.id} className="border-b">
                        <td className="px-4 py-3 text-sm font-medium">{coupon.code}</td>
                        <td className="px-4 py-3 text-sm">{coupon.coupon_type || "percentage"}</td>
                        <td className="px-4 py-3 text-sm">{coupon.value || coupon.discount_percent}%</td>
                        <td className="px-4 py-3 text-sm">{coupon.used_count}/{coupon.usage_limit}</td>
                        <td className="px-4 py-3 text-sm">{new Date(coupon.valid_until).toLocaleDateString()}</td>
                        <td className="px-4 py-3">
                          <button onClick={() => handleDeleteCoupon(coupon.id)} className="text-red-600 hover:text-red-800 text-sm">Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
""")

# --- PART 7: Customers Tab ---
f.write("""
          {tab === "customers" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <input
                  type="text"
                  placeholder="Search users..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && fetchTabData("customers")}
                  className="border rounded px-3 py-1 text-sm w-64"
                />
                <button onClick={() => openUserModal()} className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700">
                  Add User
                </button>
              </div>
              <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Name</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Email</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Role</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Status</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id} className="border-b">
                        <td className="px-4 py-3 text-sm">{user.name}</td>
                        <td className="px-4 py-3 text-sm">{user.email}</td>
                        <td className="px-4 py-3 text-sm">{user.role}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            user.is_banned ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"
                          }`}>
                            {user.is_banned ? "Banned" : "Active"}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm space-x-2">
                          <button onClick={() => openUserModal(user)} className="text-teal-600 hover:text-teal-800">Edit</button>
                          <button onClick={() => handleBanUserToggle(user.id, !user.is_banned)} className={user.is_banned ? "text-green-600" : "text-orange-600"}>
                            {user.is_banned ? "Unban" : "Ban"}
                          </button>
                          <button onClick={() => handleDeleteUser(user.id)} className="text-red-600 hover:text-red-800">Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {userModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                  <div className="bg-white rounded-lg p-6 w-full max-w-md">
                    <h3 className="text-lg font-semibold mb-4">{editingUser ? "Edit User" : "Add User"}</h3>
                    <form onSubmit={handleUserSave} className="space-y-4">
                      <input type="text" placeholder="Name" value={userForm.name} onChange={(e) => setUserForm({...userForm, name: e.target.value})} className="border rounded px-3 py-2 w-full" required />
                      <input type="email" placeholder="Email" value={userForm.email} onChange={(e) => setUserForm({...userForm, email: e.target.value})} className="border rounded px-3 py-2 w-full" required />
                      {!editingUser && <input type="password" placeholder="Password" value={userForm.password} onChange={(e) => setUserForm({...userForm, password: e.target.value})} className="border rounded px-3 py-2 w-full" required />}
                      <input type="text" placeholder="Address" value={userForm.address} onChange={(e) => setUserForm({...userForm, address: e.target.value})} className="border rounded px-3 py-2 w-full" />
                      <input type="text" placeholder="Mobile" value={userForm.mobile} onChange={(e) => setUserForm({...userForm, mobile: e.target.value})} className="border rounded px-3 py-2 w-full" />
                      <select value={userForm.role} onChange={(e) => setUserForm({...userForm, role: e.target.value})} className="border rounded px-3 py-2 w-full">
                        {ROLE_OPTIONS.map((r) => (<option key={r} value={r}>{r}</option>))}
                      </select>
                      <div className="flex justify-end space-x-3 pt-4">
                        <button type="button" onClick={() => setUserModal(false)} className="px-4 py-2 border rounded hover:bg-gray-50">Cancel</button>
                        <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700">Save</button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}
""")

# --- PART 8: Categories Tab ---
f.write("""
          {tab === "categories" && (
            <div className="space-y-4">
              <button onClick={() => openCategoryModal()} className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700">
                Add Category
              </button>
              <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Name</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Slug</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Description</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categories.map((cat) => (
                      <tr key={cat.id} className="border-b">
                        <td className="px-4 py-3 text-sm">{cat.name}</td>
                        <td className="px-4 py-3 text-sm">{cat.slug}</td>
                        <td className="px-4 py-3 text-sm">{cat.description?.substring(0, 50)}</td>
                        <td className="px-4 py-3 text-sm space-x-2">
                          <button onClick={() => openCategoryModal(cat)} className="text-teal-600 hover:text-teal-800">Edit</button>
                          <button onClick={() => handleDeleteCategory(cat.id)} className="text-red-600 hover:text-red-800">Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {categoryModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                  <div className="bg-white rounded-lg p-6 w-full max-w-md">
                    <h3 className="text-lg font-semibold mb-4">{editingCategory ? "Edit Category" : "Add Category"}</h3>
                    <form onSubmit={handleCategorySave} className="space-y-4">
                      <input type="text" placeholder="Name" value={categoryForm.name} onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})} className="border rounded px-3 py-2 w-full" required />
                      <input type="text" placeholder="Slug" value={categoryForm.slug} onChange={(e) => setCategoryForm({...categoryForm, slug: e.target.value})} className="border rounded px-3 py-2 w-full" />
                      <textarea placeholder="Description" value={categoryForm.description} onChange={(e) => setCategoryForm({...categoryForm, description: e.target.value})} className="border rounded px-3 py-2 w-full" rows="3" />
                      <input type="number" placeholder="Parent ID (optional)" value={categoryForm.parent_id} onChange={(e) => setCategoryForm({...categoryForm, parent_id: e.target.value})} className="border rounded px-3 py-2 w-full" />
                      <div className="flex justify-end space-x-3 pt-4">
                        <button type="button" onClick={() => setCategoryModal(false)} className="px-4 py-2 border rounded hover:bg-gray-50">Cancel</button>
                        <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700">Save</button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}
""")

# --- PART 9: Tax Rules Tab ---
f.write("""
          {tab === "taxes" && (
            <div className="space-y-4">
              <button onClick={() => openTaxModal()} className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700">
                Add Tax Rule
              </button>
              <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Name</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Rate (%)</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Country</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Region</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Status</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {taxRules.map((tax) => (
                      <tr key={tax.id} className="border-b">
                        <td className="px-4 py-3 text-sm">{tax.name}</td>
                        <td className="px-4 py-3 text-sm">{tax.rate}%</td>
                        <td className="px-4 py-3 text-sm">{tax.country || "N/A"}</td>
                        <td className="px-4 py-3 text-sm">{tax.region || "N/A"}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            tax.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                          }`}>
                            {tax.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm space-x-2">
                          <button onClick={() => openTaxModal(tax)} className="text-teal-600 hover:text-teal-800">Edit</button>
                          <button onClick={() => handleDeleteTax(tax.id)} className="text-red-600 hover:text-red-800">Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {taxModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                  <div className="bg-white rounded-lg p-6 w-full max-w-md">
                    <h3 className="text-lg font-semibold mb-4">{editingTax ? "Edit Tax Rule" : "Add Tax Rule"}</h3>
                    <form onSubmit={handleTaxSave} className="space-y-4">
                      <input type="text" placeholder="Name" value={taxForm.name} onChange={(e) => setTaxForm({...taxForm, name: e.target.value})} className="border rounded px-3 py-2 w-full" required />
                      <input type="number" placeholder="Rate (%)" value={taxForm.rate} onChange={(e) => setTaxForm({...taxForm, rate: e.target.value})} className="border rounded px-3 py-2 w-full" required />
                      <input type="text" placeholder="Country" value={taxForm.country} onChange={(e) => setTaxForm({...taxForm, country: e.target.value})} className="border rounded px-3 py-2 w-full" />
                      <input type="text" placeholder="Region" value={taxForm.region} onChange={(e) => setTaxForm({...taxForm, region: e.target.value})} className="border rounded px-3 py-2 w-full" />
                      <select value={taxForm.is_active} onChange={(e) => setTaxForm({...taxForm, is_active: e.target.value})} className="border rounded px-3 py-2 w-full">
                        <option value={1}>Active</option>
                        <option value={0}>Inactive</option>
                      </select>
                      <div className="flex justify-end space-x-3 pt-4">
                        <button type="button" onClick={() => setTaxModal(false)} className="px-4 py-2 border rounded hover:bg-gray-50">Cancel</button>
                        <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700">Save</button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}
""")

# --- PART 10: Draft Orders Tab ---
f.write("""
          {tab === "drafts" && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Create Draft Order</h3>
                <form onSubmit={handleDraftOrderSave} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <input type="text" placeholder="Guest Name" value={draftOrderForm.guest_name} onChange={(e) => setDraftOrderForm({...draftOrderForm, guest_name: e.target.value})} className="border rounded px-3 py-2" />
                    <input type="email" placeholder="Guest Email" value={draftOrderForm.guest_email} onChange={(e) => setDraftOrderForm({...draftOrderForm, guest_email: e.target.value})} className="border rounded px-3 py-2" />
                    <input type="text" placeholder="Guest Mobile" value={draftOrderForm.guest_mobile} onChange={(e) => setDraftOrderForm({...draftOrderForm, guest_mobile: e.target.value})} className="border rounded px-3 py-2" />
                    <select value={draftOrderForm.payment_method} onChange={(e) => setDraftOrderForm({...draftOrderForm, payment_method: e.target.value})} className="border rounded px-3 py-2">
                      <option value="card">Card</option>
                      <option value="cod">Cash on Delivery</option>
                      <option value="paypal">PayPal</option>
                    </select>
                  </div>
                  <textarea placeholder="Shipping Address" value={draftOrderForm.guest_address} onChange={(e) => setDraftOrderForm({...draftOrderForm, guest_address: e.target.value})} className="border rounded px-3 py-2 w-full" rows="2" />
                  
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-700">Order Items</h4>
                    {draftOrderForm.items.map((item, index) => (
                      <div key={index} className="grid grid-cols-3 gap-2">
                        <input type="number" placeholder="Product ID" value={item.product_id} onChange={(e) => { const items = [...draftOrderForm.items]; items[index].product_id = e.target.value; setDraftOrderForm({...draftOrderForm, items}); }} className="border rounded px-2 py-1" />
                        <input type="number" placeholder="Quantity" value={item.quantity} onChange={(e) => { const items = [...draftOrderForm.items]; items[index].quantity = e.target.value; setDraftOrderForm({...draftOrderForm, items}); }} className="border rounded px-2 py-1" />
                        <input type="number" placeholder="Unit Price" value={item.unit_price} onChange={(e) => { const items = [...draftOrderForm.items]; items[index].unit_price = e.target.value; setDraftOrderForm({...draftOrderForm, items}); }} className="border rounded px-2 py-1" />
                      </div>
                    ))}
                    <button type="button" onClick={() => setDraftOrderForm({...draftOrderForm, items: [...draftOrderForm.items, { product_id: "", quantity: "", unit_price: "" }]})} className="text-teal-600 text-sm hover:text-teal-800">
                      + Add Item
                    </button>
                  </div>
                  
                  <button type="submit" className="w-full bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700">
                    Create Draft Order
                  </button>
                </form>
              </div>
            </div>
          )}
""")

# --- PART 11: Audit Logs Tab ---
f.write("""
          {tab === "audit" && (
            <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">User</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Action</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Entity</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Details</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="border-b">
                      <td className="px-4 py-3 text-sm">{log.user_name || log.user_id}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          log.action === "CREATE" ? "bg-green-100 text-green-800" :
                          log.action === "DELETE" ? "bg-red-100 text-red-800" :
                          log.action === "BAN" ? "bg-orange-100 text-orange-800" :
                          "bg-blue-100 text-blue-800"
                        }`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{log.entity_type} #{log.entity_id}</td>
                      <td className="px-4 py-3 text-sm">{log.details}</td>
                      <td className="px-4 py-3 text-sm">{new Date(log.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
""")

# --- CLOSE ---
f.write("""
        </motion.div>
      </div>
    </div>
  );
}
""")

f.close()
print(f"✅ AdminDashboard.jsx written successfully to: {path}")