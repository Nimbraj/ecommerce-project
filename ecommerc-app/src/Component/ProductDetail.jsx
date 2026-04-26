import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { getProduct, getReviews, addReview, addToCartAPI, addToWishlist } from "../services/api";

const StarRating = ({ rating, setRating, interactive = false }) => {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => interactive && setRating && setRating(star)}
          className={`text-2xl ${star <= rating ? "text-yellow-400" : "text-gray-300"} ${interactive ? "cursor-pointer hover:scale-110" : "cursor-default"}`}
        >
          ★
        </button>
      ))}
    </div>
  );
};

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [imgZoom, setImgZoom] = useState(false);

  // Review form
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [reviewLoading, setReviewLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [p, r] = await Promise.all([
          getProduct(id),
          getReviews(id),
        ]);
        setProduct(p);
        setReviews(r);
      } catch (err) {
        setError(err.message || "Failed to load product");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  // Dynamic SEO meta tags
  useEffect(() => {
    if (product) {
      document.title = product.meta_title || `${product.title} | ShopSwift`;
      let metaDesc = document.querySelector('meta[name="description"]');
      if (!metaDesc) {
        metaDesc = document.createElement('meta');
        metaDesc.setAttribute('name', 'description');
        document.head.appendChild(metaDesc);
      }
      metaDesc.setAttribute('content', product.meta_description || product.description || `Buy ${product.title} at ShopSwift`);
    }
    return () => {
      document.title = "ShopSwift";
    };
  }, [product]);

  const handleAddToCart = async () => {
    try {
      await addToCartAPI(product.id, quantity, product);
      alert(`Added ${quantity} x "${product.title}" to cart`);
    } catch (err) {
      alert(err.message || "Failed to add to cart");
    }
  };

  const handleAddToWishlist = async () => {
    try {
      await addToWishlist(product.id);
      alert("Added to wishlist!");
    } catch (err) {
      alert("Please login to use wishlist");
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    setReviewLoading(true);
    try {
      await addReview({ product_id: Number(id), rating, comment });
      setComment("");
      setRating(5);
      const r = await getReviews(id);
      setReviews(r);
      alert("Review submitted!");
    } catch (err) {
      alert("Please login to submit a review");
    } finally {
      setReviewLoading(false);
    }
  };

  if (loading) return <div className="p-20 text-center">Loading product...</div>;
  if (error) return <div className="p-20 text-center text-red-500">{error}</div>;
  if (!product) return <div className="p-20 text-center">Product not found</div>;

  const avgRating = reviews.length
    ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
    : "No ratings yet";

  return (
    <motion.div
      className="min-h-screen bg-gray-50 pt-20 pb-10 px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      {/* Breadcrumb */}
      <nav className="max-w-6xl mx-auto mb-6 text-sm text-gray-500">
        <Link to="/" className="hover:text-teal-600">Home</Link>
        <span className="mx-2">{'>'}</span>
        <Link to="/product" className="hover:text-teal-600">Products</Link>
        <span className="mx-2">{'>'}</span>
        <span className="text-gray-800">{product.title}</span>
      </nav>

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Image */}
        <div className="relative">
          <div
            className={`rounded-2xl overflow-hidden bg-white shadow-lg cursor-${imgZoom ? "zoom-in" : "pointer"}`}
            onClick={() => setImgZoom(!imgZoom)}
          >
            <img
              src={`http://localhost:8000${product.image_url}`}
              alt={product.title}
              className={`w-full object-cover transition-transform duration-500 ${imgZoom ? "scale-150" : "scale-100"}`}
              style={{ height: imgZoom ? "auto" : "400px" }}
              onError={(e) => { e.target.src = '/assets/8.jpg'; }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">Click image to {imgZoom ? "zoom out" : "zoom in"}</p>
        </div>

        {/* Details */}
        <div className="space-y-4">
          <span className="inline-block px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-sm font-medium">
            {product.category}
          </span>
          <h1 className="text-3xl font-bold text-gray-800">{product.title}</h1>

          <div className="flex items-center gap-3">
            <StarRating rating={Math.round(Number(avgRating) || 0)} />
            <span className="text-gray-500 text-sm">({avgRating}) · {reviews.length} reviews</span>
          </div>

          <p className="text-4xl font-bold text-teal-600">₹{product.price}</p>

          <div className="bg-white p-4 rounded-xl shadow-sm">
            <h3 className="font-semibold text-gray-700 mb-2">Description</h3>
            <p className="text-gray-600 leading-relaxed">{product.description || "No description available."}</p>
          </div>

          <div className="bg-white p-4 rounded-xl shadow-sm">
            <h3 className="font-semibold text-gray-700 mb-2">Specifications</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><span className="font-medium">Category:</span> {product.category}</li>
              <li><span className="font-medium">Price:</span> ₹{product.price}</li>
              <li><span className="font-medium">Featured:</span> {product.is_featured ? "Yes" : "No"}</li>
            </ul>
          </div>

          {/* Quantity + Actions */}
          <div className="flex items-center gap-4 pt-2">
            <div className="flex items-center border rounded-lg overflow-hidden">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200"
              >−</button>
              <span className="px-4 py-2 font-medium">{quantity}</span>
              <button
                onClick={() => setQuantity(quantity + 1)}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200"
              >+</button>
            </div>
            <button
              onClick={handleAddToCart}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              Add to Cart
            </button>
            <button
              onClick={handleAddToWishlist}
              className="px-4 py-3 border border-teal-500 text-teal-600 rounded-lg hover:bg-teal-50 transition"
            >
              ♥ Wishlist
            </button>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="max-w-6xl mx-auto mt-14">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Customer Reviews</h2>

        {/* Add Review */}
        <form onSubmit={handleSubmitReview} className="bg-white p-6 rounded-xl shadow-sm mb-8">
          <h3 className="font-semibold text-gray-700 mb-3">Write a Review</h3>
          <div className="mb-3">
            <label className="block text-sm text-gray-600 mb-1">Rating</label>
            <StarRating rating={rating} setRating={setRating} interactive />
          </div>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Share your experience..."
            className="w-full border rounded-lg p-3 mb-3 focus:ring-2 focus:ring-teal-400 outline-none"
            rows={3}
          />
          <button
            type="submit"
            disabled={reviewLoading}
            className="bg-teal-600 text-white px-6 py-2 rounded-lg hover:bg-teal-700 transition disabled:opacity-50"
          >
            {reviewLoading ? "Submitting..." : "Submit Review"}
          </button>
        </form>

        {/* Review List */}
        {reviews.length === 0 ? (
          <p className="text-gray-500">No reviews yet. Be the first to review!</p>
        ) : (
          <div className="space-y-4">
            {reviews.map((review) => (
              <div key={review.id} className="bg-white p-5 rounded-xl shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 font-bold">
                      {(review.user_name || "U").charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">{review.user_name || "Anonymous"}</p>
                      <p className="text-xs text-gray-400">{new Date(review.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <StarRating rating={review.rating} />
                </div>
                <p className="text-gray-600">{review.comment}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

