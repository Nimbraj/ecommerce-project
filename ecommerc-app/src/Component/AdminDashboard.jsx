import React, { useState, useEffect } from "react";
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

  const [productForm, setProductForm] = useState({ 
    title: "", sku: "", slug: "", description: "", price: "", category: "", 
    image_url: "", status: "active", stock_quantity: "100", low_stock_threshold: "10", is_featured: 0 
  });
  const [couponForm, setCouponForm] = useState({ 
    code: "", coupon_type: "percentage", value: "", min_order_value: "", 
    max_discount: "", usage_limit: "", valid_until: "" 
  });
  const [userForm, setUserForm] = useState({ 
    name: "", email: "", password: "", address: "", mobile: "", role: "customer" 
  });
  const [categoryForm, setCategoryForm] = useState({ 
    name: "", slug: "", description: "", parent_id: "" 
  });
  const [taxForm, setTaxForm] = useState({ 
    name: "", rate: "", country: "", region: "", is_active: 1 
  });
  const [draftOrderForm, setDraftOrderForm] = useState({ 
    items: [{ product_id: "", quantity: "", unit_price: "" }], 
    guest_email: "", guest_name: "", guest_mobile: "", guest_address: "", payment_method: "card" 
  });
  const [inventoryEdits, setInventoryEdits] = useState({});

  // Fetch all initial data
  useEffect(() => { 
    fetchAll(); 
  }, []);

  const fetchAll = async () => {
    setLoading(true); 
    setError("");
    try {
      const [a, o, l, p, c] = await Promise.all([
        getAdminAnalytics(), 
        getAllOrders(), 
        getLowStock(), 
        getAdminProducts(), 
        getCoupons()
      ]);
      setAnalytics(a); 
      setOrders(o); 
      setLowStock(l); 
      setProducts(p); 
      setCoupons(c);
    } catch (err) { 
      setError(err.message || "Failed to load data"); 
      if (err.message?.includes("Admin")) navigate("/"); 
    } finally { 
      setLoading(false); 
    }
  };

  const fetchTabData = async (tabName) => {
    try {
      if (tabName === "customers") { 
        const u = await getUsers(userSearch); 
        setUsers(u); 
      } else if (tabName === "categories") { 
        const cats = await getCategories(); 
        setCategories(cats); 
      } else if (tabName === "taxes") { 
        const t = await getTaxRules(); 
        setTaxRules(t); 
      } else if (tabName === "audit") { 
        const logs = await getAuditLogs(); 
        setAuditLogs(logs); 
      } else if (tabName === "products") { 
        const p = await getAdminProducts(
          productFilter.category || undefined, 
          productFilter.status || undefined
        ); 
        setProducts(p); 
      }
    } catch (err) { 
      alert(err.message); 
    }
  };

  useEffect(() => { 
    if (["customers", "categories", "taxes", "audit", "products"].includes(tab)) {
      fetchTabData(tab); 
    }
  }, [tab]);

  // Handler functions
  const handleStatusChange = async (orderId, newStatus) => {
    try { 
      await updateOrderStatus(orderId, newStatus); 
      setOrders((prev) => prev.map((o) => (
        o.id === orderId ? { ...o, status: newStatus } : o
      ))); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleInventoryUpdate = async (productId, newStock, threshold) => {
    try { 
      await updateInventory(productId, Number(newStock), Number(threshold)); 
      setProducts((prev) => prev.map((p) => (
        p.id === productId ? { 
          ...p, 
          stock_quantity: Number(newStock), 
          low_stock_threshold: Number(threshold) 
        } : p
      ))); 
      const l = await getLowStock(); 
      setLowStock(l); 
      alert("Inventory updated successfully"); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleCreateCoupon = async (e) => {
    e.preventDefault(); 
    try { 
      const payload = { 
        ...couponForm, 
        value: Number(couponForm.value), 
        min_order_value: Number(couponForm.min_order_value || 0), 
        max_discount: couponForm.max_discount ? Number(couponForm.max_discount) : null, 
        usage_limit: Number(couponForm.usage_limit || 1), 
        valid_until: couponForm.valid_until ? new Date(couponForm.valid_until).toISOString() : null 
      }; 
      await createCoupon(payload); 
      setCouponForm({ 
        code: "", coupon_type: "percentage", value: "", min_order_value: "", 
        max_discount: "", usage_limit: "", valid_until: "" 
      }); 
      const c = await getCoupons(); 
      setCoupons(c); 
      alert("Coupon created!"); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleDeleteCoupon = async (id) => {
    if (!window.confirm("Delete this coupon?")) return; 
    try { 
      await deleteCoupon(id); 
      setCoupons((prev) => prev.filter((c) => c.id !== id)); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  // Product CRUD
  const openProductModal = (product = null) => {
    if (product) { 
      setEditingProduct(product); 
      setProductForm({ 
        title: product.title || "", 
        sku: product.sku || "", 
        slug: product.slug || "", 
        description: product.description || "", 
        price: product.price || "", 
        category: product.category || "", 
        image_url: product.image_url || "", 
        status: product.status || "active", 
        stock_quantity: product.stock_quantity || "100", 
        low_stock_threshold: product.low_stock_threshold || "10", 
        is_featured: product.is_featured || 0 
      }); 
    } else { 
      setEditingProduct(null); 
      setProductForm({ 
        title: "", sku: "", slug: "", description: "", price: "", category: "", 
        image_url: "", status: "active", stock_quantity: "100", 
        low_stock_threshold: "10", is_featured: 0 
      }); 
    } 
    setProductModal(true);
  };

  const handleProductSave = async (e) => {
    e.preventDefault(); 
    try { 
      const payload = { 
        ...productForm, 
        price: Number(productForm.price), 
        stock_quantity: Number(productForm.stock_quantity), 
        low_stock_threshold: Number(productForm.low_stock_threshold), 
        is_featured: Number(productForm.is_featured) 
      }; 
      if (editingProduct) { 
        await updateProduct(editingProduct.id, payload); 
      } else { 
        await createProduct(payload); 
      } 
      setProductModal(false); 
      const p = await getAdminProducts(
        productFilter.category || undefined, 
        productFilter.status || undefined
      ); 
      setProducts(p); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleDeleteProduct = async (id) => {
    if (!window.confirm("Delete this product?")) return; 
    try { 
      await deleteProduct(id); 
      setProducts((prev) => prev.filter((p) => p.id !== id)); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  // User CRUD
  const openUserModal = (user = null) => {
    if (user) { 
      setEditingUser(user); 
      setUserForm({ 
        name: user.name || "", 
        email: user.email || "", 
        password: "", 
        address: user.address || "", 
        mobile: user.mobile || "", 
        role: user.role || "customer" 
      }); 
    } else { 
      setEditingUser(null); 
      setUserForm({ 
        name: "", email: "", password: "", address: "", mobile: "", role: "customer" 
      }); 
    } 
    setUserModal(true);
  };

  const handleUserSave = async (e) => {
    e.preventDefault(); 
    try { 
      if (editingUser) { 
        const payload = { ...userForm }; 
        if (!payload.password) delete payload.password; 
        await updateUserAdmin(editingUser.id, payload); 
      } else { 
        await createUserAdmin(userForm); 
      } 
      setUserModal(false); 
      const u = await getUsers(userSearch); 
      setUsers(u); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleDeleteUser = async (id) => {
    if (!window.confirm("Delete this user?")) return; 
    try { 
      await deleteUserAdmin(id); 
      setUsers((prev) => prev.filter((u) => u.id !== id)); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleBanUserToggle = async (id, ban) => {
    try { 
      if (ban) await banUser(id); 
      else await unbanUser(id); 
      const u = await getUsers(userSearch); 
      setUsers(u); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  // Category CRUD
  const openCategoryModal = (cat = null) => {
    if (cat) { 
      setEditingCategory(cat); 
      setCategoryForm({ 
        name: cat.name || "", 
        slug: cat.slug || "", 
        description: cat.description || "", 
        parent_id: cat.parent_id || "" 
      }); 
    } else { 
      setEditingCategory(null); 
      setCategoryForm({ name: "", slug: "", description: "", parent_id: "" }); 
    } 
    setCategoryModal(true);
  };

  const handleCategorySave = async (e) => {
    e.preventDefault(); 
    try { 
      const payload = { ...categoryForm }; 
      if (!payload.parent_id) delete payload.parent_id; 
      if (editingCategory) { 
        await updateCategory(editingCategory.id, payload); 
      } else { 
        await createCategory(payload); 
      } 
      setCategoryModal(false); 
      const cats = await getCategories(); 
      setCategories(cats); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm("Delete this category?")) return; 
    try { 
      await deleteCategory(id); 
      setCategories((prev) => prev.filter((c) => c.id !== id)); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  // Tax Rule CRUD
  const openTaxModal = (tax = null) => {
    if (tax) { 
      setEditingTax(tax); 
      setTaxForm({ 
        name: tax.name || "", 
        rate: tax.rate || "", 
        country: tax.country || "", 
        region: tax.region || "", 
        is_active: tax.is_active ?? 1 
      }); 
    } else { 
      setEditingTax(null); 
      setTaxForm({ name: "", rate: "", country: "", region: "", is_active: 1 }); 
    } 
    setTaxModal(true);
  };

  const handleTaxSave = async (e) => {
    e.preventDefault(); 
    try { 
      const payload = { 
        ...taxForm, 
        rate: Number(taxForm.rate), 
        is_active: Number(taxForm.is_active) 
      }; 
      if (editingTax) { 
        await updateTaxRule(editingTax.id, payload); 
      } else { 
        await createTaxRule(payload); 
      } 
      setTaxModal(false); 
      const t = await getTaxRules(); 
      setTaxRules(t); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleDeleteTax = async (id) => {
    if (!window.confirm("Delete this tax rule?")) return; 
    try { 
      await deleteTaxRule(id); 
      setTaxRules((prev) => prev.filter((t) => t.id !== id)); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  // Order actions
  const handleDraftOrderSave = async (e) => {
    e.preventDefault(); 
    try { 
      const payload = { 
        ...draftOrderForm, 
        items: draftOrderForm.items.map((item) => ({ 
          product_id: Number(item.product_id), 
          quantity: Number(item.quantity), 
          unit_price: Number(item.unit_price) 
        })) 
      }; 
      await createDraftOrder(payload); 
      setDraftOrderModal(false); 
      setDraftOrderForm({ 
        items: [{ product_id: "", quantity: "", unit_price: "" }], 
        guest_email: "", guest_name: "", guest_mobile: "", 
        guest_address: "", payment_method: "card" 
      }); 
      const o = await getAllOrders(); 
      setOrders(o); 
      alert("Draft order created!"); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm("Cancel this order?")) return; 
    try { 
      await cancelOrder(orderId); 
      const o = await getAllOrders(); 
      setOrders(o); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  const handleRefundOrder = async (orderId) => {
    if (!window.confirm("Refund this order?")) return; 
    try { 
      await refundOrder(orderId); 
      const o = await getAllOrders(); 
      setOrders(o); 
    } catch (err) { 
      alert(err.message); 
    }
  };

  // Status badge helper
  const statusBadge = (status) => {
    const map = {
      pending: "bg-yellow-100 text-yellow-800",
      confirmed: "bg-blue-100 text-blue-800",
      processing: "bg-purple-100 text-purple-800",
      shipped: "bg-indigo-100 text-indigo-800",
      delivered: "bg-green-100 text-green-800",
      cancelled: "bg-gray-100 text-gray-800",
      active: "bg-green-100 text-green-800",
      draft: "bg-yellow-100 text-yellow-800",
      archived: "bg-gray-100 text-gray-800",
      out_of_stock: "bg-red-100 text-red-800",
    };
    return map[status] || "bg-gray-100 text-gray-800";
  };

  // Loading & Error states
  if (loading) return <div className="pt-24 text-center text-gray-600">Loading dashboard...</div>;
  if (error) return <div className="pt-24 text-center text-red-500">Error: {error}</div>;

  // Data parsing
  const summary = analytics?.sales_summary || {};
  const topProducts = analytics?.top_products || [];
  const recentOrders = analytics?.recent_orders || [];
  const lowStockItems = analytics?.low_stock_items || [];

  // Tab configuration
  const tabs = [
    { id: "analytics", label: "Analytics" },
    { id: "products", label: "Products" },
    { id: "orders", label: "Orders" },
    { id: "customers", label: "Customers" },
    { id: "inventory", label: "Inventory" },
    { id: "coupons", label: "Coupons" },
    { id: "categories", label: "Categories" },
    { id: "taxes", label: "Tax Rules" },
    { id: "audit", label: "Audit Logs" },
  ];

  return (
    <motion.div 
      className="min-h-screen bg-gray-50 pt-20 pb-10 px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>
          <button
            onClick={() => navigate("/")}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition"
          >
            Back to Store
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 overflow-x-auto flex-wrap">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition ${
                tab === t.id 
                  ? "bg-teal-600 text-white" 
                  : "bg-white text-gray-600 border hover:bg-gray-50"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {tab === "analytics" && (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: "Total Orders", value: summary.total_orders || 0 },
                { label: "Total Revenue", value: `₹${(summary.total_revenue || 0).toLocaleString()}` },
                { label: "Today Orders", value: summary.today_orders || 0 },
                { label: "Today Revenue", value: `₹${(summary.today_revenue || 0).toLocaleString()}` }
              ].map((kpi) => (
                <div key={kpi.label} className="bg-white p-5 rounded-xl shadow-sm">
                  <p className="text-sm text-gray-500">{kpi.label}</p>
                  <p className="text-2xl font-bold text-gray-800 mt-1">{kpi.value}</p>
                </div>
              ))}
            </div>

            {/* Low Stock Alert */}
            {lowStockItems.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                <h3 className="font-semibold text-red-700 mb-2">
                  ⚠️ Low Stock Alerts ({lowStockItems.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {lowStockItems.map((item) => (
                    <span key={item.id} className="text-sm bg-white border border-red-200 text-red-700 px-3 py-1 rounded-full">
                      {item.title}: {item.stock_quantity} left
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-5 rounded-xl shadow-sm">
                <h3 className="font-semibold text-gray-700 mb-4">Top Selling Products</h3>
                {topProducts.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={topProducts}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="title" tick={{ fontSize: 12 }} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="total_sold" fill="#0d9488" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-center text-gray-400 py-10">No data available</p>
                )}
              </div>
              <div className="bg-white p-5 rounded-xl shadow-sm">
                <h3 className="font-semibold text-gray-700 mb-4">Revenue Distribution</h3>
                {topProducts.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={topProducts}
                        dataKey="total_revenue"
                        nameKey="title"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {topProducts.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-center text-gray-400 py-10">No data available</p>
                )}
              </div>
            </div>

            {/* Recent Orders Table */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-5 border-b">
                <h3 className="font-semibold text-gray-700">Recent Orders</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-600">
                    <tr>
                      <th className="text-left px-5 py-3">Order ID</th>
                      <th className="text-left px-5 py-3">Status</th>
                      <th className="text-left px-5 py-3">Total</th>
                      <th className="text-left px-5 py-3">Items</th>
                      <th className="text-left px-5 py-3">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentOrders.map((o) => (
                      <tr key={o.id} className="border-b hover:bg-gray-50">
                        <td className="px-5 py-3 font-medium">#{o.id}</td>
                        <td className="px-5 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(o.status)}`}>
                            {o.status}
                          </span>
                        </td>
                        <td className="px-5 py-3">₹{Number(o.total).toFixed(2)}</td>
                        <td className="px-5 py-3">{o.item_count}</td>
                        <td className="px-5 py-3">{new Date(o.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                    {recentOrders.length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-5 py-6 text-center text-gray-400">No orders yet</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {tab === "products" && (
          <div className="space-y-4">
            {/* Filters & Add Button */}
            <div className="flex flex-wrap gap-2 items-center justify-between">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Filter by category"
                  value={productFilter.category}
                  onChange={(e) => setProductFilter({ ...productFilter, category: e.target.value })}
                  className="border rounded-lg px-3 py-2 text-sm"
                />
                <select
                  value={productFilter.status}
                  onChange={(e) => setProductFilter({ ...productFilter, status: e.target.value })}
                  className="border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">All Status</option>
                  {PRODUCT_STATUS_OPTIONS.map((s) => (
                    <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
                  ))}
                </select>
                <button
                  onClick={() => fetchTabData("products")}
                  className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700"
                >
                  Filter
                </button>
              </div>
              <button
                onClick={() => openProductModal()}
                className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700"
              >
                + Add Product
              </button>
            </div>

            {/* Products Table */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-600">
                    <tr>
                      <th className="text-left px-5 py-3">Title</th>
                      <th className="text-left px-5 py-3">SKU</th>
                      <th className="text-left px-5 py-3">Price</th>
                      <th className="text-left px-5 py-3">Category</th>
                      <th className="text-left px-5 py-3">Status</th>
                      <th className="text-left px-5 py-3">Stock</th>
                      <th className="text-left px-5 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p) => (
                      <tr key={p.id} className="border-b hover:bg-gray-50">
                        <td className="px-5 py-3 font-medium">{p.title}</td>
                        <td className="px-5 py-3">{p.sku || "—"}</td>
                        <td className="px-5 py-3">₹{p.price}</td>
                        <td className="px-5 py-3">{p.category}</td>
                        <td className="px-5 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(p.status)}`}>
                            {p.status}
                          </span>
                        </td>
                        <td className="px-5 py-3">{p.stock_quantity}</td>
                        <td className="px-5 py-3 space-x-2">
                          <button
                            onClick={() => openProductModal(p)}
                            className="text-teal-600 hover:underline text-xs"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteProduct(p.id)}
                            className="text-red-600 hover:underline text-xs"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {products.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-5 py-6 text-center text-gray-400">
                          No products found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {tab === "orders" && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                onClick={() => setDraftOrderModal(true)}
                className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700"
              >
                + Draft Order
              </button>
            </div>
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-5 border-b flex justify-between items-center">
                <h3 className="font-semibold text-gray-700">All Orders</h3>
                <button onClick={fetchAll} className="text-sm text-teal-600 hover:underline">
                  Refresh
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-600">
                    <tr>
                      <th className="text-left px-5 py-3">Order ID</th>
                      <th className="text-left px-5 py-3">Customer</th>
                      <th className="text-left px-5 py-3">Status</th>
                      <th className="text-left px-5 py-3">Total</th>
                      <th className="text-left px-5 py-3">Date</th>
                      <th className="text-left px-5 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map((o) => (
                      <tr key={o.id} className="border-b hover:bg-gray-50">
                        <td className="px-5 py-3 font-medium">#{o.id}</td>
                        <td className="px-5 py-3">{o.user?.name || "N/A"}</td>
                        <td className="px-5 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(o.status)}`}>
                            {o.status}
                          </span>
                        </td>
                        <td className="px-5 py-3">₹{Number(o.total).toFixed(2)}</td>
                        <td className="px-5 py-3">{new Date(o.created_at).toLocaleDateString()}</td>
                        <td className="px-5 py-3 space-x-2">
                          <select
                            value={o.status}
                            onChange={(e) => handleStatusChange(o.id, e.target.value)}
                            className="border rounded px-2 py-1 text-xs"
                          >
                            {STATUS_OPTIONS.map((s) => (
                              <option key={s} value={s}>{s}</option>
                            ))}
                          </select>
                          {o.status !== "cancelled" && o.status !== "delivered" && (
                            <button
                              onClick={() => handleCancelOrder(o.id)}
                              className="text-red-600 hover:underline text-xs"
                            >
                              Cancel
                            </button>
                          )}
                          {o.status === "delivered" && (
                            <button
                              onClick={() => handleRefundOrder(o.id)}
                              className="text-orange-600 hover:underline text-xs"
                            >
                              Refund
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                    {orders.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-5 py-6 text-center text-gray-400">
                          No orders yet
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {tab === "customers" && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2 items-center justify-between">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Search users..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  className="border rounded-lg px-3 py-2 text-sm"
                />
                <button
                  onClick={() => fetchTabData("customers")}
                  className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700"
                >
                  Search
                </button>
              </div>
              <button
                onClick={() => openUserModal()}
                className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700"
              >
                + Add User
              </button>
            </div>
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-600">
                    <tr>
                      <th className="text-left px-5 py-3">Name</th>
                      <th className="text-left px-5 py-3">Email</th>
                      <th className="text-left px-5 py-3">Role</th>
                      <th className="text-left px-5 py-3">Status</th>
                      <th className="text-left px-5 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className="border-b hover:bg-gray-50">
                        <td className="px-5 py-3 font-medium">{u.name}</td>
                        <td className="px-5 py-3">{u.email}</td>
                        <td className="px-5 py-3 capitalize">{u.role}</td>
                        <td className="px-5 py-3">
                          {u.is_banned ? (
                            <span className="text-red-600 font-medium">Banned</span>
                          ) : (
                            <span className="text-green-600 font-medium">Active</span>
                          )}
                        </td>
                        <td className="px-5 py-3 space-x-2">
                          <button
                            onClick={() => openUserModal(u)}
                            className="text-teal-600 hover:underline text-xs"
                          >
                            Edit
                          </button>
                          {u.is_banned ? (
                            <button
                              onClick={() => handleBanUserToggle(u.id, false)}
                              className="text-green-600 hover:underline text-xs"
                            >
                              Unban
                            </button>
                          ) : (
                            <button
                              onClick={() => handleBanUserToggle(u.id, true)}
                              className="text-orange-600 hover:underline text-xs"
                            >
                              Ban
                            </button>
                          )}
                          <button
                            onClick={() => handleDeleteUser(u.id)}
                            className="text-red-600 hover:underline text-xs"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {users.length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-5 py-6 text-center text-gray-400">
                          No users found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {tab === "inventory" && (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="p-5 border-b">
              <h3 className="font-semibold text-gray-700">Inventory Management</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="text-left px-5 py-3">Product</th>
                    <th className="text-left px-5 py-3">Category</th>
                    <th className="text-left px-5 py-3">Stock</th>
                    <th className="text-left px-5 py-3">Threshold</th>
                    <th className="text-left px-5 py-3">Status</th>
                    <th className="text-left px-5 py-3">Update</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p) => {
                    const isLow = p.stock_quantity <= (p.low_stock_threshold || 10);
                    const edit = inventoryEdits[p.id] || { 
                      stock: p.stock_quantity, 
                      threshold: p.low_stock_threshold || 10 
                    };
                    return (
                      <tr key={p.id} className="border-b hover:bg-gray-50">
                        <td className="px-5 py-3 font-medium">{p.title}</td>
                        <td className="px-5 py-3">{p.category}</td>
                        <td className={`px-5 py-3 font-medium ${isLow ? "text-red-600" : ""}`}>
                          {p.stock_quantity}
                        </td>
                        <td className="px-5 py-3">{p.low_stock_threshold || 10}</td>
                        <td className="px-5 py-3">
                          {isLow ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              Low Stock
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              In Stock
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-3">
                          <div className="flex gap-1 items-center">
                            <input
                              type="number"
                              value={edit.stock}
                              onChange={(e) => setInventoryEdits({ 
                                ...inventoryEdits, 
                                [p.id]: { ...edit, stock: e.target.value } 
                              })}
                              className="border rounded px-2 py-1 w-20 text-xs"
                              placeholder="Stock"
                            />
                            <input
                              type="number"
                              value={edit.threshold}
                              onChange={(e) => setInventoryEdits({ 
                                ...inventoryEdits, 
                                [p.id]: { ...edit, threshold: e.target.value } 
                              })}
                              className="border rounded px-2 py-1 w-20 text-xs"
                              placeholder="Min"
                            />
                            <button
                              onClick={() => handleInventoryUpdate(p.id, edit.stock, edit.threshold)}
                              className="bg-teal-600 text-white px-3 py-1 rounded text-xs hover:bg-teal-700"
                            >
                              Update
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                  {products.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-5 py-6 text-center text-gray-400">
                        No products found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {tab === "coupons" && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="font-semibold text-gray-700 mb-4">Create New Coupon</h3>
              <form onSubmit={handleCreateCoupon} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <input 
                  type="text" 
                  placeholder="Coupon Code" 
                  value={couponForm.code} 
                  onChange={(e) => setCouponForm({...couponForm, code: e.target.value})} 
                  className="border rounded-lg px-3 py-2 text-sm" 
                  required 
                />
                <select 
                  value={couponForm.coupon_type} 
                  onChange={(e) => setCouponForm({...couponForm, coupon_type: e.target.value})} 
                  className="border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                </select>
                <input 
                  type="number" 
                  placeholder="Value" 
                  value={couponForm.value} 
                  onChange={(e) => setCouponForm({...couponForm, value: e.target.value})} 
                  className="border rounded-lg px-3 py-2 text-sm" 
                  required 
                />
                <input 
                  type="number" 
                  placeholder="Min Order Amount" 
                  value={couponForm.min_order_value} 
                  onChange={(e) => setCouponForm({...couponForm, min_order_value: e.target.value})} 
                  className="border rounded-lg px-3 py-2 text-sm" 
                />
                <input 
                  type="number" 
                  placeholder="Max Discount" 
                  value={couponForm.max_discount} 
                  onChange={(e) => setCouponForm({...couponForm, max_discount: e.target.value})} 
                  className="border rounded-lg px-3 py-2 text-sm" 
                />
                <input 
                  type="number" 
                  placeholder="Usage Limit" 
                  value={couponForm.usage_limit} 
                  onChange={(e) => setCouponForm({...couponForm, usage_limit: e.target.value})} 
                  className="border rounded-lg px-3 py-2 text-sm" 
                />
                <input 
                  type="datetime-local" 
                  value={couponForm.valid_until} 
                  onChange={(e) => setCouponForm({...couponForm, valid_until: e.target.value})} 
                  className="border rounded-lg px-3 py-2 text-sm" 
                />
                <button 
                  type="submit" 
                  className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700 sm:col-span-2 lg:col-span-1"
                >
                  Create Coupon
                </button>
              </form>
            </div>
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-5 border-b">
                <h3 className="font-semibold text-gray-700">All Coupons</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-600">
                    <tr>
                      <th className="text-left px-5 py-3">Code</th>
                      <th className="text-left px-5 py-3">Type</th>
                      <th className="text-left px-5 py-3">Value</th>
                      <th className="text-left px-5 py-3">Usage</th>
                      <th className="text-left px-5 py-3">Valid Until</th>
                      <th className="text-left px-5 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {coupons.map((c) => (
                      <tr key={c.id} className="border-b hover:bg-gray-50">
                        <td className="px-5 py-3 font-medium">{c.code}</td>
                        <td className="px-5 py-3 capitalize">{c.coupon_type || "percentage"}</td>
                        <td className="px-5 py-3">
                          {c.value || c.discount_percent}{c.coupon_type === "fixed" ? "₹" : "%"}
                        </td>
                        <td className="px-5 py-3">{c.used_count || 0}/{c.usage_limit || "∞"}</td>
                        <td className="px-5 py-3">
                          {c.valid_until ? new Date(c.valid_until).toLocaleDateString() : "—"}
                        </td>
                        <td className="px-5 py-3">
                          <button 
                            onClick={() => handleDeleteCoupon(c.id)} 
                            className="text-red-600 hover:underline text-xs"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {coupons.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-5 py-6 text-center text-gray-400">
                          No coupons created
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {tab === "categories" && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button 
                onClick={() => openCategoryModal()} 
                className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700"
              >
                + Add Category
              </button>
            </div>
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-600">
                    <tr>
                      <th className="text-left px-5 py-3">Name</th>
                      <th className="text-left px-5 py-3">Slug</th>
                      <th className="text-left px-5 py-3">Description</th>
                      <th className="text-left px-5 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categories.map((cat) => (
                      <tr key={cat.id} className="border-b hover:bg-gray-50">
                        <td className="px-5 py-3 font-medium">{cat.name}</td>
                        <td className="px-5 py-3">{cat.slug || "—"}</td>
                        <td className="px-5 py-3 max-w-xs truncate">{cat.description || "—"}</td>
                        <td className="px-5 py-3 space-x-2">
                          <button 
                            onClick={() => openCategoryModal(cat)} 
                            className="text-teal-600 hover:underline text-xs"
                          >
                            Edit
                          </button>
                          <button 
                            onClick={() => handleDeleteCategory(cat.id)} 
                            className="text-red-600 hover:underline text-xs"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {categories.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-5 py-6 text-center text-gray-400">
                          No categories found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {tab === "taxes" && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button 
                onClick={() => openTaxModal()} 
                className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700"
              >
                + Add Tax Rule
              </button>
            </div>
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-600">
                    <tr>
                      <th className="text-left px-5 py-3">Name</th>
                      <th className="text-left px-5 py-3">Rate</th>
                      <th className="text-left px-5 py-3">Country</th>
                      <th className="text-left px-5 py-3">Region</th>
                      <th className="text-left px-5 py-3">Status</th>
                      <th className="text-left px-5 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {taxRules.map((tax) => (
                      <tr key={tax.id} className="border-b hover:bg-gray-50">
                        <td className="px-5 py-3 font-medium">{tax.name}</td>
                        <td className="px-5 py-3">{tax.rate}%</td>
                        <td className="px-5 py-3">{tax.country || "—"}</td>
                        <td className="px-5 py-3">{tax.region || "—"}</td>
                        <td className="px-5 py-3">
                          {tax.is_active ? (
                            <span className="text-green-600 font-medium">Active</span>
                          ) : (
                            <span className="text-red-600">Inactive</span>
                          )}
                        </td>
                        <td className="px-5 py-3 space-x-2">
                          <button 
                            onClick={() => openTaxModal(tax)} 
                            className="text-teal-600 hover:underline text-xs"
                          >
                            Edit
                          </button>
                          <button 
                            onClick={() => handleDeleteTax(tax.id)} 
                            className="text-red-600 hover:underline text-xs"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {taxRules.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-5 py-6 text-center text-gray-400">
                          No tax rules found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {tab === "audit" && (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="p-5 border-b">
              <h3 className="font-semibold text-gray-700">Audit Logs</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="text-left px-5 py-3">User</th>
                    <th className="text-left px-5 py-3">Action</th>
                    <th className="text-left px-5 py-3">Entity</th>
                    <th className="text-left px-5 py-3">Details</th>
                    <th className="text-left px-5 py-3">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="border-b hover:bg-gray-50">
                      <td className="px-5 py-3">{log.user_name || `User #${log.user_id}`}</td>
                      <td className="px-5 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(log.action?.toLowerCase())}`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-5 py-3">{log.entity_type} #{log.entity_id}</td>
                      <td className="px-5 py-3 max-w-xs truncate">{log.details}</td>
                      <td className="px-5 py-3">{new Date(log.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                  {auditLogs.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-5 py-6 text-center text-gray-400">
                        No audit logs
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Product Modal */}
        {productModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">
                {editingProduct ? "Edit Product" : "Add Product"}
              </h3>
              <form onSubmit={handleProductSave} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <input type="text" placeholder="Title *" value={productForm.title} onChange={(e) => setProductForm({...productForm, title: e.target.value})} className="border rounded-lg px-3 py-2" required />
                  <input type="text" placeholder="SKU" value={productForm.sku} onChange={(e) => setProductForm({...productForm, sku: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <input type="text" placeholder="Slug" value={productForm.slug} onChange={(e) => setProductForm({...productForm, slug: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <input type="number" placeholder="Price *" value={productForm.price} onChange={(e) => setProductForm({...productForm, price: e.target.value})} className="border rounded-lg px-3 py-2" required />
                  <input type="text" placeholder="Category" value={productForm.category} onChange={(e) => setProductForm({...productForm, category: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <input type="url" placeholder="Image URL" value={productForm.image_url} onChange={(e) => setProductForm({...productForm, image_url: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <select value={productForm.status} onChange={(e) => setProductForm({...productForm, status: e.target.value})} className="border rounded-lg px-3 py-2">
                    {PRODUCT_STATUS_OPTIONS.map((s) => (<option key={s} value={s}>{s.replace(/_/g, " ")}</option>))}
                  </select>
                  <input type="number" placeholder="Stock Quantity" value={productForm.stock_quantity} onChange={(e) => setProductForm({...productForm, stock_quantity: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <input type="number" placeholder="Low Stock Threshold" value={productForm.low_stock_threshold} onChange={(e) => setProductForm({...productForm, low_stock_threshold: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <select value={productForm.is_featured} onChange={(e) => setProductForm({...productForm, is_featured: e.target.value})} className="border rounded-lg px-3 py-2">
                    <option value={0}>Not Featured</option>
                    <option value={1}>Featured</option>
                  </select>
                </div>
                <textarea placeholder="Description" value={productForm.description} onChange={(e) => setProductForm({...productForm, description: e.target.value})} className="border rounded-lg px-3 py-2 w-full" rows="3" />
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setProductModal(false)} className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50">Cancel</button>
                  <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">Save</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* User Modal */}
        {userModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">
                {editingUser ? "Edit User" : "Add User"}
              </h3>
              <form onSubmit={handleUserSave} className="space-y-4">
                <input type="text" placeholder="Name *" value={userForm.name} onChange={(e) => setUserForm({...userForm, name: e.target.value})} className="border rounded-lg px-3 py-2 w-full" required />
                <input type="email" placeholder="Email *" value={userForm.email} onChange={(e) => setUserForm({...userForm, email: e.target.value})} className="border rounded-lg px-3 py-2 w-full" required />
                <input type="password" placeholder={editingUser ? "New Password (optional)" : "Password *"} value={userForm.password} onChange={(e) => setUserForm({...userForm, password: e.target.value})} className="border rounded-lg px-3 py-2 w-full" required={!editingUser} />
                <input type="text" placeholder="Address" value={userForm.address} onChange={(e) => setUserForm({...userForm, address: e.target.value})} className="border rounded-lg px-3 py-2 w-full" />
                <input type="text" placeholder="Mobile" value={userForm.mobile} onChange={(e) => setUserForm({...userForm, mobile: e.target.value})} className="border rounded-lg px-3 py-2 w-full" />
                <select value={userForm.role} onChange={(e) => setUserForm({...userForm, role: e.target.value})} className="border rounded-lg px-3 py-2 w-full">
                  {ROLE_OPTIONS.map((r) => (<option key={r} value={r}>{r}</option>))}
                </select>
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setUserModal(false)} className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50">Cancel</button>
                  <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">Save</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Category Modal */}
        {categoryModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">
                {editingCategory ? "Edit Category" : "Add Category"}
              </h3>
              <form onSubmit={handleCategorySave} className="space-y-4">
                <input type="text" placeholder="Name *" value={categoryForm.name} onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})} className="border rounded-lg px-3 py-2 w-full" required />
                <input type="text" placeholder="Slug" value={categoryForm.slug} onChange={(e) => setCategoryForm({...categoryForm, slug: e.target.value})} className="border rounded-lg px-3 py-2 w-full" />
                <textarea placeholder="Description" value={categoryForm.description} onChange={(e) => setCategoryForm({...categoryForm, description: e.target.value})} className="border rounded-lg px-3 py-2 w-full" rows="3" />
                <input type="number" placeholder="Parent ID (optional)" value={categoryForm.parent_id} onChange={(e) => setCategoryForm({...categoryForm, parent_id: e.target.value})} className="border rounded-lg px-3 py-2 w-full" />
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setCategoryModal(false)} className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50">Cancel</button>
                  <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">Save</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Tax Modal */}
        {taxModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">
                {editingTax ? "Edit Tax Rule" : "Add Tax Rule"}
              </h3>
              <form onSubmit={handleTaxSave} className="space-y-4">
                <input type="text" placeholder="Name *" value={taxForm.name} onChange={(e) => setTaxForm({...taxForm, name: e.target.value})} className="border rounded-lg px-3 py-2 w-full" required />
                <input type="number" placeholder="Rate (%) *" value={taxForm.rate} onChange={(e) => setTaxForm({...taxForm, rate: e.target.value})} className="border rounded-lg px-3 py-2 w-full" required />
                <input type="text" placeholder="Country" value={taxForm.country} onChange={(e) => setTaxForm({...taxForm, country: e.target.value})} className="border rounded-lg px-3 py-2 w-full" />
                <input type="text" placeholder="Region" value={taxForm.region} onChange={(e) => setTaxForm({...taxForm, region: e.target.value})} className="border rounded-lg px-3 py-2 w-full" />
                <select value={taxForm.is_active} onChange={(e) => setTaxForm({...taxForm, is_active: Number(e.target.value)})} className="border rounded-lg px-3 py-2 w-full">
                  <option value={1}>Active</option>
                  <option value={0}>Inactive</option>
                </select>
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setTaxModal(false)} className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50">Cancel</button>
                  <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">Save</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Draft Order Modal */}
        {draftOrderModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Create Draft Order</h3>
              <form onSubmit={handleDraftOrderSave} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input type="text" placeholder="Guest Name" value={draftOrderForm.guest_name} onChange={(e) => setDraftOrderForm({...draftOrderForm, guest_name: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <input type="email" placeholder="Guest Email" value={draftOrderForm.guest_email} onChange={(e) => setDraftOrderForm({...draftOrderForm, guest_email: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <input type="text" placeholder="Guest Mobile" value={draftOrderForm.guest_mobile} onChange={(e) => setDraftOrderForm({...draftOrderForm, guest_mobile: e.target.value})} className="border rounded-lg px-3 py-2" />
                  <select value={draftOrderForm.payment_method} onChange={(e) => setDraftOrderForm({...draftOrderForm, payment_method: e.target.value})} className="border rounded-lg px-3 py-2">
                    <option value="card">Card</option>
                    <option value="cod">Cash on Delivery</option>
                    <option value="paypal">PayPal</option>
                  </select>
                </div>
                <textarea placeholder="Shipping Address" value={draftOrderForm.guest_address} onChange={(e) => setDraftOrderForm({...draftOrderForm, guest_address: e.target.value})} className="border rounded-lg px-3 py-2 w-full" rows="2" />
                
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">Order Items</h4>
                  {draftOrderForm.items.map((item, index) => (
                    <div key={index} className="grid grid-cols-3 gap-2">
                      <input type="number" placeholder="Product ID" value={item.product_id} onChange={(e) => { const items = [...draftOrderForm.items]; items[index].product_id = e.target.value; setDraftOrderForm({...draftOrderForm, items}); }} className="border rounded-lg px-2 py-1 text-sm" />
                      <input type="number" placeholder="Quantity" value={item.quantity} onChange={(e) => { const items = [...draftOrderForm.items]; items[index].quantity = e.target.value; setDraftOrderForm({...draftOrderForm, items}); }} className="border rounded-lg px-2 py-1 text-sm" />
                      <input type="number" placeholder="Unit Price" value={item.unit_price} onChange={(e) => { const items = [...draftOrderForm.items]; items[index].unit_price = e.target.value; setDraftOrderForm({...draftOrderForm, items}); }} className="border rounded-lg px-2 py-1 text-sm" />
                    </div>
                  ))}
                  <button type="button" onClick={() => setDraftOrderForm({...draftOrderForm, items: [...draftOrderForm.items, { product_id: "", quantity: "", unit_price: "" }]})} className="text-teal-600 text-sm hover:text-teal-800 font-medium">
                    + Add Another Item
                  </button>
                </div>
                
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setDraftOrderModal(false)} className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50">Cancel</button>
                  <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">Create Draft Order</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}