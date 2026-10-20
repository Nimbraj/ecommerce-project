import React, { useState } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { loginUser, login2FA, mergeGuestCart } from "../services/api";

const formVariants = {
  hidden: { opacity: 0, y: -50 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

const LoginForm = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isAdminLogin = searchParams.get("account") === "admin";
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [requiresTwoFactor, setRequiresTwoFactor] = useState(false);
  const [otp, setOtp] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = requiresTwoFactor
        ? await login2FA(formData.email, formData.password, otp)
        : await loginUser(formData);
      localStorage.setItem("token", data.access_token);
      let cartWarning = "";
      try {
        await mergeGuestCart();
      } catch (syncError) {
        cartWarning = ` Your saved cart could not be synced (${syncError.message}); you can still use your account.`;
      }
      window.dispatchEvent(new Event("auth-changed"));
      alert(`Login successful!${cartWarning}`);
      navigate("/");
    } catch (err) {
      if (err.message === "Two-factor authentication required") {
        setRequiresTwoFactor(true);
        setError("Enter the code from your authenticator app.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen h-screen flex items-center justify-center bg-gradient-to-r from-indigo-500 to-purple-600">
      <motion.div
        className="w-full max-w-md p-8 space-y-6 bg-white rounded-2xl shadow-2xl"
        variants={formVariants}
        initial="hidden"
        animate="visible"
      >
        <h2 className="text-2xl font-bold text-center text-gray-800">
          {isAdminLogin ? "Admin Login" : "Login to Your Account"}
        </h2>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {requiresTwoFactor && (
            <div>
              <label htmlFor="otp" className="block text-sm font-medium text-gray-700">Authenticator code</label>
              <input id="otp" inputMode="numeric" autoComplete="one-time-code" value={otp} onChange={(event) => setOtp(event.target.value)} required className="w-full px-4 py-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          )}

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 mt-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <motion.button
            type="submit"
            whileTap={{ scale: 0.95 }}
            disabled={loading}
            className="w-full py-2 font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition duration-300 disabled:opacity-50"
          >
            {loading ? "Logging in..." : requiresTwoFactor ? "Verify and Login" : "Login"}
          </motion.button>
        </form>

        <p className="text-sm text-center text-gray-600">
          Don’t have an account?{" "}
          <Link to="/register" className="text-indigo-600 hover:underline">
            Sign Up
          </Link>
        </p>
        {!isAdminLogin && (
          <p className="text-sm text-center text-gray-600">
            Admin?{" "}
            <Link to="/login?account=admin" className="text-indigo-600 hover:underline">
              Admin login
            </Link>
          </p>
        )}
      </motion.div>
    </div>
  );
};

export default LoginForm;
