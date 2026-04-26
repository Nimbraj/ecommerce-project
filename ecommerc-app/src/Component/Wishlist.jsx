import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { getWishlist, removeFromWishlist, addToCartAPI } from "../services/api";

export default function Wishlist() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const fetchWishlist = async () => {
    try {
      const data = await getWishlist();
      setItems(data);
    } catch (err) {
      setError("Please login to view your wishlist");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWishlist();
  }, []);

  const handleRemove = async (id) => {
    try {
      await removeFromWishlist(id);
      fetchWishlist();
    } catch (err) {
      alert("Failed to remove");
    }
  };

  const handleMoveToCart = async (product) => {
    try {
      await addToCartAPI(product.id, 1, product);
      alert("Moved to cart!");
    } catch (err) {
      alert(err.message || "Failed");
    }
  };

  if (loading) return <div className="p-20 text-center pt-20">Loading wishlist...</div>;
  if (error) return <div className="p-20 text-center text-red-500 pt-20">{error}</div>;

  return (
    <motion.div
      className="min-h-screen bg-gray-50 pt-20 pb-10 px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">My Wishlist</h1>

        {items.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-10 text-center">
            <p className="text-gray-500 mb-4">Your wishlist is empty.</p>
            <Link to="/product" className="text-teal-600 hover:underline font-medium">Browse Products</Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {items.map((item) => (
              <div key={item.id} className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition">
                <img
                  src={`http://localhost:8000${item.product.image_url}`}
                  alt={item.product.title}
                  className="w-full h-48 object-cover cursor-pointer"
                  onClick={() => navigate(`/product/${item.product.id}`)}
                  onError={(e) => { e.target.src = '/assets/8.jpg'; }}
                />
                <div className="p-4">
                  <h3 className="font-semibold text-gray-800 mb-1">{item.product.title}</h3>
                  <p className="text-teal-600 font-bold mb-3">₹{item.product.price}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleMoveToCart(item.product)}
                      className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm hover:bg-blue-700 transition"
                    >
                      Move to Cart
                    </button>
                    <button
                      onClick={() => handleRemove(item.id)}
                      className="px-3 py-2 border border-red-300 text-red-500 rounded-lg hover:bg-red-50 transition"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

