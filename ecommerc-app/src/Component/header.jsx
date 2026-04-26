import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaShoppingCart, FaHeart, FaSearch } from "react-icons/fa";
import { getCurrentUser, searchProducts, getCartCount } from "../services/api";

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showSearch, setShowSearch] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  const navigate = useNavigate();

  const checkAuth = () => {
    const token = localStorage.getItem("token");
    if (token) {
      getCurrentUser()
        .then((data) => setUser(data))
        .catch(() => { localStorage.removeItem("token"); setUser(null); });
    } else {
      setUser(null);
    }
    const count = getCartCount();
    setCartCount(count || 0);
  };

  useEffect(() => {
    checkAuth();
    window.addEventListener("auth-changed", checkAuth);
    window.addEventListener("focus", checkAuth);
    return () => {
      window.removeEventListener("auth-changed", checkAuth);
      window.removeEventListener("focus", checkAuth);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    window.dispatchEvent(new Event("auth-changed"));
    navigate("/");
  };

  const handleSearchChange = async (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (q.length >= 2) {
      try {
        const results = await searchProducts(q);
        setSearchResults(results.slice(0, 6));
        setShowSearch(true);
      } catch {
        setSearchResults([]);
      }
    } else {
      setSearchResults([]);
      setShowSearch(false);
    }
  };

  const handleSearchSelect = (id) => {
    setSearchQuery("");
    setShowSearch(false);
    navigate(`/product/${id}`);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/product?q=${encodeURIComponent(searchQuery)}`);
      setShowSearch(false);
    }
  };

  return (
    <header className="fixed top-0 left-0 w-full bg-[#cdebdd] shadow z-50">
      <div className="mx-auto flex h-16 max-w-screen-xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center text-teal-600 font-bold text-xl" aria-label="Home">
          ShopSwift
        </Link>

        {/* Search Bar */}
        <div className="hidden md:flex flex-1 mx-8 max-w-md relative">
          <form onSubmit={handleSearchSubmit} className="w-full relative">
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              onBlur={() => setTimeout(() => setShowSearch(false), 200)}
              placeholder="Search products..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-400 bg-white"
            />
            <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            {showSearch && searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 bg-white border rounded-lg shadow-lg mt-1 overflow-hidden z-50">
                {searchResults.map((p) => (
                  <div
                    key={p.id}
                    onMouseDown={() => handleSearchSelect(p.id)}
                    className="flex items-center gap-3 px-4 py-2 hover:bg-gray-50 cursor-pointer"
                  >
                    <img src={`http://localhost:8000${p.image_url}`} alt={p.title} className="w-8 h-8 object-cover rounded" onError={(e) => { e.target.src = '/assets/8.jpg'; }} />
                    <div>
                      <p className="text-sm font-medium text-gray-800">{p.title}</p>
                      <p className="text-xs text-gray-500">₹{p.price}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </form>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:block">
          <ul className="flex items-center gap-5 text-sm text-gray-600">
            <li><Link to="/" className="hover:text-teal-600 transition">Home</Link></li>
            <li><Link to="/about" className="hover:text-teal-600 transition">About</Link></li>
            <li><Link to="/product" className="hover:text-teal-600 transition">Product</Link></li>
          </ul>
        </nav>

        {/* Right Side Buttons */}
        <div className="flex items-center gap-4">
          {/* Wishlist */}
          <Link to="/wishlist" className="relative text-gray-700 hover:text-teal-600 hidden sm:block">
            <FaHeart className="text-xl" />
          </Link>

          {/* Cart Icon */}
          <Link to="/cart" className="relative text-gray-700 hover:text-teal-600">
            <FaShoppingCart className="text-xl" />
            {cartCount > 0 && (
              <span className="absolute -top-2 -right-2 text-xs bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </Link>

          {user ? (
            <>
              {user.is_admin ? (
                <Link to="/admin" className="hidden sm:block text-sm font-medium text-teal-700 hover:underline">
                  Admin
                </Link>
              ) : null}
              <Link to="/orders" className="hidden sm:block text-sm text-gray-700 hover:text-teal-600 transition">
                Orders
              </Link>
              <span className="text-sm text-gray-700 hidden sm:block">Hi, {user.name}</span>
              <button
                onClick={handleLogout}
                className="rounded-md bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-600 transition"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700 transition"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="hidden sm:block rounded-md bg-white border border-teal-500 px-4 py-2 text-sm font-medium text-teal-600 hover:bg-teal-100 transition"
              >
                Register
              </Link>
            </>
          )}

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden rounded-md bg-gray-100 p-2 text-gray-600 hover:text-gray-800 transition"
            aria-label="Toggle menu"
            aria-expanded={isMobileMenuOpen}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <nav id="mobile-menu" className="md:hidden px-4 pb-4">
          {/* Mobile Search */}
          <form onSubmit={handleSearchSubmit} className="relative mb-3">
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search products..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-400 bg-white"
            />
            <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          </form>
          <ul className="space-y-2 text-sm text-gray-700">
            <li><Link to="/" className="block hover:text-teal-600">Home</Link></li>
            <li><Link to="/about" className="block hover:text-teal-600">About</Link></li>
            <li><Link to="/product" className="block hover:text-teal-600">Product</Link></li>
            <li><Link to="/wishlist" className="block hover:text-teal-600">Wishlist</Link></li>
            <li><Link to="/cart" className="block hover:text-teal-600">Cart</Link></li>
            <li><Link to="/login" className="block hover:text-teal-600">Login</Link></li>
            <li><Link to="/register" className="block hover:text-teal-600">Register</Link></li>
          </ul>
        </nav>
      )}
    </header>
  );
};

export default Header;

