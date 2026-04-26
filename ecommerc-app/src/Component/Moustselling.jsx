import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getProducts, addToCartAPI } from "../services/api";

const categoryColor = {
  "Most Selling": "bg-rose-100 text-rose-700",
  "Trending": "bg-yellow-100 text-yellow-700",
  "Regular": "bg-gray-100 text-gray-800",
};

export default function MostSelling() {
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

  const addToCart = async (productId) => {
    try {
      const product = products.find((p) => p.id === productId);
      await addToCartAPI(productId, 1, product);
      alert("Added to cart!");
    } catch (err) {
      alert(err.message || "Failed to add item");
    }
  };

  if (loading) return <div className="py-20 text-center">Loading products...</div>;
  if (error) return <div className="py-20 text-center text-red-500">{error}</div>;

  return (
    <div className="mt-10 bg-gray-100 py-10 px-6">
      <h2 className="text-3xl font-bold text-center mb-10 text-gray-800">
        Products
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {products.map((product) => (
          <article
            key={product.id}
            className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-md hover:shadow-xl hover:scale-105 transition-transform duration-300"
          >
            <img
              src={`http://localhost:8000${product.image_url}`}
              alt={`Image of ${product.title}`}
              className="h-56 w-full object-cover"
              onError={(e) => { e.target.src = '/assets/21.jpg'; }}
            />

            <div className="p-4 sm:p-6">
              <span
                className={`inline-block mb-2 px-2 py-1 text-xs font-semibold rounded ${categoryColor[product.category] || "bg-gray-100 text-gray-800"}`}
              >
                {product.category}
              </span>

              <h3 className="text-lg font-medium text-gray-900">
                {product.title}
              </h3>

              <p className="mt-2 text-sm text-gray-500 line-clamp-3">
                {product.description}
              </p>

              <div className="mt-4 flex items-center justify-between gap-2">
                <span className="text-xl font-semibold text-teal-600">
                  ₹{product.price}
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => navigate(`/product/${product.id}`)}
                    className="bg-teal-600 text-white px-3 py-1 rounded hover:bg-teal-700 transition text-sm"
                  >
                    Details
                  </button>
                  <button
                    onClick={() => addToCart(product.id)}
                    className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition text-sm"
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
