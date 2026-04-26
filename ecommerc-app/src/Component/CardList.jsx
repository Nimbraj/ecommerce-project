import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { getProducts, addToCartAPI } from "../services/api";

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0 },
};

const CardList = () => {
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await getProducts();
        setProducts(data);
      } catch (err) {
        setError("Failed to load products");
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  const handleCardClick = (index) => {
    setSelectedIndex(index === selectedIndex ? null : index);
  };

  const addToCart = async (product) => {
    try {
      await addToCartAPI(product.id, 1, product);
      alert(`Added "${product.title}" to cart.`);
    } catch (err) {
      alert(err.message || "Failed to add item");
    }
  };

  if (loading) return <div className="p-20 text-center">Loading products...</div>;
  if (error) return <div className="p-20 text-center text-red-500">{error}</div>;

  return (
    <motion.div
      className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-6 bg-gray-100 min-h-screen pt-20"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {products.map((product, index) => (
        <motion.div
          key={product.id}
          variants={cardVariants}
          onClick={() => handleCardClick(index)}
          className="rounded-2xl bg-white shadow-lg hover:shadow-2xl transition-shadow cursor-pointer overflow-hidden"
        >
          <img
            src={`http://localhost:8000${product.image_url}`}
            alt={product.title}
            className="w-full h-64 object-cover bg-gray-200"
            onError={(e) => { e.target.src = '/assets/8.jpg'; }}
          />
          <div className="p-4 space-y-2">
            <h2 className="text-lg font-semibold text-gray-800">{product.title}</h2>
            <p className="text-sm text-gray-500">{product.category}</p>
            <p className="text-md font-bold text-blue-600">₹{product.price}</p>

            {selectedIndex === index && (
              <div className="mt-2 text-sm text-gray-700">
                <p>{product.description}</p>
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      addToCart(product);
                    }}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                  >
                    Add to Cart
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/product/${product.id}`);
                    }}
                    className="flex-1 bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700 transition"
                  >
                    View Details
                  </button>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
};

export default CardList;
