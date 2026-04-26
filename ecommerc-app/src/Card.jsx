import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getCartItems, removeFromCartAPI, clearCartAPI } from "./services/api";

export default function Cart() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const fetchCart = async () => {
    try {
      const data = await getCartItems();
      setItems(data);
    } catch (err) {
      setError(err.message || "Failed to load cart");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleRemove = async (cartId) => {
    try {
      await removeFromCartAPI(cartId);
      fetchCart();
    } catch (err) {
      alert("Failed to remove item");
    }
  };

  const handleClear = async () => {
    try {
      await clearCartAPI();
      fetchCart();
    } catch (err) {
      alert("Failed to clear cart");
    }
  };

  const total = items.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);

  if (loading) return <div className="p-6">Loading cart...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6 min-h-screen pt-20">
      <h2 className="text-xl font-bold mb-4">Your Cart</h2>
      {items.length === 0 ? (
        <p>Cart is empty 🛒</p>
      ) : (
        <>
          <ul className="space-y-2">
            {items.map((item) => (
              <li key={item.id} className="flex justify-between items-center bg-white p-3 rounded shadow">
                <div>
                  <span className="font-medium">{item.product.title}</span>
                  <span className="text-gray-500 ml-2">x{item.quantity}</span>
                  <span className="text-blue-600 ml-2">₹{item.product.price * item.quantity}</span>
                </div>
                <button onClick={() => handleRemove(item.id)} className="text-red-500 hover:text-red-700">Remove</button>
              </li>
            ))}
          </ul>
          <p className="mt-4 font-semibold text-lg">Total: ₹{total}</p>
          <div className="flex gap-3 mt-4">
            <button onClick={handleClear} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition">
              Clear Cart
            </button>
            <button onClick={() => navigate('/checkout')} className="bg-teal-600 text-white px-6 py-2 rounded hover:bg-teal-700 transition">
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
    </div>
  );
}
