import React, { useState } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../services/api";

const RegisterForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    address: "",
    email: "",
    password: "",
    mobile: "",
    admin_key: "",
  });
  const [accountType, setAccountType] = useState("user");

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errors[e.target.name]) {
      setErrors((prevErrors) => ({ ...prevErrors, [e.target.name]: "" }));
    }
    setApiError("");
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.address.trim()) newErrors.address = "Address is required";
    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email address is invalid";
    }
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }
    if (!formData.mobile) {
      newErrors.mobile = "Mobile number is required";
    } else if (!/^\d{10}$/.test(formData.mobile)) {
      newErrors.mobile = "Mobile number must be 10 digits";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError("");
    if (!validateForm()) return;

    const payload = { ...formData };
    if (accountType === "user") {
      payload.admin_key = "";
    }

    setLoading(true);
    try {
      await registerUser(payload);
      alert("Registration successful! Please login.");
      navigate("/login");
    } catch (err) {
      setApiError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen min-h-screen flex items-center justify-center bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-10">
      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md bg-white p-8 mt-10 rounded-2xl shadow-2xl"
      >
        <h2 className="text-3xl font-bold text-center text-teal-700 mb-2">Register</h2>
        <p className="text-center text-gray-500 text-sm mb-6">Create a new account</p>

        {apiError && (
          <div className="bg-red-100 text-red-700 p-3 rounded-lg text-sm mb-4">
            {apiError}
          </div>
        )}

        {/* Account Type Toggle */}
        <div className="flex rounded-lg bg-gray-100 p-1 mb-6">
          <button
            type="button"
            onClick={() => setAccountType("user")}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition ${
              accountType === "user"
                ? "bg-white text-teal-700 shadow"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            User Account
          </button>
          <button
            type="button"
            onClick={() => setAccountType("admin")}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition ${
              accountType === "admin"
                ? "bg-white text-teal-700 shadow"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Admin Account
          </button>
        </div>

        {/* Name */}
        <div className="mb-4">
          <label htmlFor="name" className="block text-sm font-medium mb-1">Name</label>
          <input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
          />
          {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
        </div>

        {/* Address */}
        <div className="mb-4">
          <label htmlFor="address" className="block text-sm font-medium mb-1">Address</label>
          <input
            id="address"
            name="address"
            type="text"
            value={formData.address}
            onChange={handleChange}
            className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
          />
          {errors.address && <p className="text-red-500 text-xs mt-1">{errors.address}</p>}
        </div>

        {/* Email */}
        <div className="mb-4">
          <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
          />
          {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
        </div>

        {/* Password */}
        <div className="mb-4">
          <label htmlFor="password" className="block text-sm font-medium mb-1">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
          />
          {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
        </div>

        {/* Mobile */}
        <div className="mb-4">
          <label htmlFor="mobile" className="block text-sm font-medium mb-1">Mobile No.</label>
          <input
            id="mobile"
            name="mobile"
            type="tel"
            maxLength={10}
            pattern="\d*"
            value={formData.mobile}
            onChange={handleChange}
            className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
          />
          {errors.mobile && <p className="text-red-500 text-xs mt-1">{errors.mobile}</p>}
        </div>

        {/* Admin Key (only for admin accounts) */}
        {accountType === "admin" && (
          <div className="mb-6">
            <label htmlFor="admin_key" className="block text-sm font-medium mb-1">
              Admin Secret Key
            </label>
            <input
              id="admin_key"
              name="admin_key"
              type="password"
              value={formData.admin_key}
              onChange={handleChange}
              placeholder="Enter admin secret key"
              className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
            />
            <p className="text-xs text-gray-400 mt-1">
              Contact your system administrator for the secret key.
            </p>
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-amber-400 py-2 rounded-lg text-white font-semibold hover:bg-amber-500 transition duration-300 disabled:opacity-50"
        >
          {loading ? "Registering..." : `Register as ${accountType === "admin" ? "Admin" : "User"}`}
        </button>

        <p className="text-center mt-4 text-sm">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Login
          </Link>
        </p>
      </motion.form>
    </div>
  );
};

export default RegisterForm;

