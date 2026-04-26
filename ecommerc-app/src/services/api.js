const API_BASE_URL = 'http://localhost:8000/api';

const getToken = () => localStorage.getItem('token');

// ============== GUEST CART HELPERS ==============
const GUEST_CART_KEY = 'guest_cart';

const getGuestCart = () => {
  try {
    return JSON.parse(localStorage.getItem(GUEST_CART_KEY)) || [];
  } catch {
    return [];
  }
};

const saveGuestCart = (cart) => {
  localStorage.setItem(GUEST_CART_KEY, JSON.stringify(cart));
};

const addToGuestCart = (product, quantity = 1) => {
  const cart = getGuestCart();
  const existing = cart.find((item) => item.product_id === product.id);
  if (existing) {
    existing.quantity += quantity;
  } else {
    cart.push({
      id: Date.now() + Math.random(),
      product_id: product.id,
      quantity,
      product,
    });
  }
  saveGuestCart(cart);
  return cart;
};

const removeFromGuestCart = (cartId) => {
  const cart = getGuestCart().filter((item) => item.id !== cartId);
  saveGuestCart(cart);
  return cart;
};

const clearGuestCart = () => {
  localStorage.removeItem(GUEST_CART_KEY);
  return [];
};

export const getCartCount = () => {
  if (getToken()) {
    return null;
  }
  return getGuestCart().reduce((sum, item) => sum + item.quantity, 0);
};

const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(getToken() && { 'Authorization': `Bearer ${getToken()}` }),
      ...options.headers,
    },
    ...options,
  };

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }

  const response = await fetch(url, config);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Something went wrong');
  }

  return data;
};

// ============== AUTH APIs ==============
export const registerUser = (userData) => apiRequest('/register', {
  method: 'POST',
  body: userData,
});

export const loginUser = (credentials) => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.email);
  formData.append('password', credentials.password);

  return fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  }).then(async (res) => {
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');
    return data;
  });
};

export const getCurrentUser = () => apiRequest('/me');

// ============== 2FA APIs ==============
export const setup2FA = () => apiRequest('/2fa/setup', { method: 'POST' });

export const verify2FA = (token) => apiRequest('/2fa/verify', {
  method: 'POST',
  body: { token },
});

export const login2FA = (email, password, token) => apiRequest('/2fa/login-verify', {
  method: 'POST',
  body: { email, password, token },
});

// ============== PRODUCT APIs ==============
export const getProducts = (category) => {
  const query = category ? `?category=${encodeURIComponent(category)}` : '';
  return apiRequest(`/products${query}`);
};

export const getProduct = (id) => apiRequest(`/products/${id}`);

export const createProduct = (productData) => apiRequest('/products', {
  method: 'POST',
  body: productData,
});

export const updateProduct = (id, productData) => apiRequest(`/products/${id}`, {
  method: 'PUT',
  body: productData,
});

export const deleteProduct = (id) => apiRequest(`/products/${id}`, {
  method: 'DELETE',
});

export const searchProducts = (query) => apiRequest(`/search?q=${encodeURIComponent(query)}`);

// ============== ADMIN PRODUCT APIs ==============
export const getAdminProducts = (category, status) => {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (status) params.append('status', status);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiRequest(`/admin/products${query}`);
};

// ============== CART APIs ==============
export const getCartItems = async () => {
  if (!getToken()) {
    return getGuestCart();
  }
  return apiRequest('/cart');
};

export const addToCartAPI = async (productId, quantity = 1, product = null) => {
  if (!getToken()) {
    if (!product) {
      product = await getProduct(productId);
    }
    return addToGuestCart(product, quantity);
  }
  return apiRequest('/cart', {
    method: 'POST',
    body: { product_id: productId, quantity },
  });
};

export const updateCartItemAPI = (cartId, quantity) => apiRequest(`/cart/${cartId}`, {
  method: 'PUT',
  body: { quantity },
});

export const removeFromCartAPI = async (cartId) => {
  if (!getToken()) {
    return removeFromGuestCart(cartId);
  }
  return apiRequest(`/cart/${cartId}`, {
    method: 'DELETE',
  });
};

export const clearCartAPI = async () => {
  if (!getToken()) {
    return clearGuestCart();
  }
  return apiRequest('/cart', {
    method: 'DELETE',
  });
};

// ============== REVIEW APIs ==============
export const getReviews = (productId) => apiRequest(`/products/${productId}/reviews`);

export const addReview = (reviewData) => apiRequest('/reviews', {
  method: 'POST',
  body: reviewData,
});

export const deleteReview = (reviewId) => apiRequest(`/reviews/${reviewId}`, {
  method: 'DELETE',
});

// ============== WISHLIST APIs ==============
export const getWishlist = () => apiRequest('/wishlist');

export const addToWishlist = (productId) => apiRequest(`/wishlist/${productId}`, {
  method: 'POST',
});

export const removeFromWishlist = (wishlistId) => apiRequest(`/wishlist/${wishlistId}`, {
  method: 'DELETE',
});

// ============== ORDER APIs ==============
export const createOrder = (orderData) => apiRequest('/orders', {
  method: 'POST',
  body: orderData,
});

export const getMyOrders = () => apiRequest('/orders/my');

export const getOrder = (orderId) => apiRequest(`/orders/${orderId}`);

export const getAllOrders = () => apiRequest('/orders');

export const updateOrderStatus = (orderId, status) => apiRequest(`/orders/${orderId}/status`, {
  method: 'PUT',
  body: { status },
});

export const createDraftOrder = (orderData) => apiRequest('/admin/orders/draft', {
  method: 'POST',
  body: orderData,
});

export const cancelOrder = (orderId) => apiRequest(`/admin/orders/${orderId}/cancel`, {
  method: 'POST',
});

export const refundOrder = (orderId) => apiRequest(`/admin/orders/${orderId}/refund`, {
  method: 'POST',
});

// ============== COUPON APIs ==============
export const getCoupons = () => apiRequest('/coupons');

export const createCoupon = (couponData) => apiRequest('/coupons', {
  method: 'POST',
  body: couponData,
});

export const validateCoupon = (code, orderTotal) => apiRequest('/coupons/validate', {
  method: 'POST',
  body: { code, order_total: orderTotal },
});

export const deleteCoupon = (couponId) => apiRequest(`/coupons/${couponId}`, {
  method: 'DELETE',
});

// ============== INVENTORY / ADMIN APIs ==============
export const updateInventory = (productId, stockQuantity, lowStockThreshold) =>
  apiRequest(`/products/${productId}/inventory`, {
    method: 'PUT',
    body: { stock_quantity: stockQuantity, low_stock_threshold: lowStockThreshold },
  });

export const getLowStock = () => apiRequest('/inventory/low-stock');

export const getAdminAnalytics = () => apiRequest('/admin/analytics');

// ============== USER MANAGEMENT APIs ==============
export const getUsers = (search) => {
  const query = search ? `?search=${encodeURIComponent(search)}` : '';
  return apiRequest(`/admin/users${query}`);
};

export const createUserAdmin = (userData) => apiRequest('/admin/users', {
  method: 'POST',
  body: userData,
});

export const updateUserAdmin = (userId, userData) => apiRequest(`/admin/users/${userId}`, {
  method: 'PUT',
  body: userData,
});

export const deleteUserAdmin = (userId) => apiRequest(`/admin/users/${userId}`, {
  method: 'DELETE',
});

export const banUser = (userId) => apiRequest(`/admin/users/${userId}/ban`, {
  method: 'POST',
});

export const unbanUser = (userId) => apiRequest(`/admin/users/${userId}/unban`, {
  method: 'POST',
});

// ============== CATEGORY APIs ==============
export const getCategories = () => apiRequest('/admin/categories');

export const createCategory = (categoryData) => apiRequest('/admin/categories', {
  method: 'POST',
  body: categoryData,
});

export const updateCategory = (categoryId, categoryData) => apiRequest(`/admin/categories/${categoryId}`, {
  method: 'PUT',
  body: categoryData,
});

export const deleteCategory = (categoryId) => apiRequest(`/admin/categories/${categoryId}`, {
  method: 'DELETE',
});

// ============== TAX RULE APIs ==============
export const getTaxRules = () => apiRequest('/admin/tax-rules');

export const createTaxRule = (taxData) => apiRequest('/admin/tax-rules', {
  method: 'POST',
  body: taxData,
});

export const updateTaxRule = (taxId, taxData) => apiRequest(`/admin/tax-rules/${taxId}`, {
  method: 'PUT',
  body: taxData,
});

export const deleteTaxRule = (taxId) => apiRequest(`/admin/tax-rules/${taxId}`, {
  method: 'DELETE',
});

// ============== AUDIT LOG APIs ==============
export const getAuditLogs = () => apiRequest('/admin/audit-logs');

