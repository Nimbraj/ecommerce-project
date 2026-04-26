import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { getCartItems, clearCartAPI, createOrder, validateCoupon } from "../services/api";

const paymentMethods = [
  { id: "card", label: "Credit / Debit Card", icon: "💳" },
  { id: "upi", label: "UPI / Google Pay / PhonePe", icon: "📱" },
  { id: "wallet", label: "Digital Wallet (Paytm)", icon: "👛" },
  { id: "cod", label: "Cash on Delivery", icon: "💵" },
  { id: "bnpl", label: "Buy Now, Pay Later (Klarna)", icon: "⏳" },
];

export default function Checkout() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState(1);

  // Guest checkout fields
  const [guestInfo, setGuestInfo] = useState({
    name: "",
    email: "",
    address: "",
    mobile: "",
  });
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [processing, setProcessing] = useState(false);

  // Coupon
  const [couponCode, setCouponCode] = useState("");
  const [couponData, setCouponData] = useState(null);
  const [couponLoading, setCouponLoading] = useState(false);

  // Order result
  const [placedOrder, setPlacedOrder] = useState(null);

  useEffect(() => {
    getCartItems()
      .then((data) => setItems(data))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const subtotal = items.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
  const tax = Math.round(subtotal * 0.18 * 100) / 100;
  const discount = couponData?.discount || 0;
  const total = Math.max(0, Math.round((subtotal + tax - discount) * 100) / 100);

  const handleGuestChange = (e) => {
    setGuestInfo({ ...guestInfo, [e.target.name]: e.target.value });
  };

  const handleApplyCoupon = async () => {
    if (!couponCode.trim()) return;
    setCouponLoading(true);
    try {
      const result = await validateCoupon(couponCode.trim(), subtotal);
      if (result.valid) {
        setCouponData(result);
      } else {
        alert(result.message);
        setCouponData(null);
      }
    } catch (err) {
      alert(err.message || "Failed to validate coupon");
      setCouponData(null);
    } finally {
      setCouponLoading(false);
    }
  };

  const handlePlaceOrder = async () => {
    if (!guestInfo.name || !guestInfo.email || !guestInfo.address || !guestInfo.mobile) {
      alert("Please fill in all shipping details");
      return;
    }
    if (items.length === 0) {
      alert("Your cart is empty");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please login to place an order");
      navigate("/login");
      return;
    }

    setProcessing(true);
    try {
      const orderPayload = {
        items: items.map((item) => ({
          product_id: item.product_id || item.product.id,
          quantity: item.quantity,
          unit_price: item.product.price,
        })),
        guest_email: guestInfo.email,
        guest_name: guestInfo.name,
        guest_mobile: guestInfo.mobile,
        guest_address: guestInfo.address,
        payment_method: paymentMethod,
        coupon_code: couponData ? couponCode.trim() : null,
      };

      const order = await createOrder(orderPayload);
      setPlacedOrder(order);
      setStep(3);
    } catch (err) {
      alert(err.message || "Failed to place order");
    } finally {
      setProcessing(false);
    }
  };

  if (loading) return <div className="p-20 text-center">Loading checkout...</div>;

  return (
    <motion.div
      className="min-h-screen bg-gray-50 pt-20 pb-10 px-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Checkout</h1>

        {/* Step indicator */}
        <div className="flex items-center mb-8">
          {["Cart Review", "Shipping & Payment", "Confirmation"].map((s, i) => (
            <React.Fragment key={s}>
              <div className={`flex-1 text-center py-2 rounded-lg font-medium ${step === i + 1 ? "bg-teal-600 text-white" : step > i + 1 ? "bg-teal-100 text-teal-700" : "bg-gray-200 text-gray-500"}`}>
                {i + 1}. {s}
              </div>
              {i < 2 && <div className="w-4" />}
            </React.Fragment>
          ))}
        </div>

        {step === 1 && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
            {items.length === 0 ? (
              <p className="text-gray-500">Your cart is empty. <button onClick={() => navigate("/product")} className="text-teal-600 underline">Go shopping</button></p>
            ) : (
              <>
                <ul className="space-y-3 mb-6">
                  {items.map((item) => (
                    <li key={item.id} className="flex justify-between items-center border-b pb-3">
                      <div className="flex items-center gap-4">
                        <img src={`http://localhost:8000${item.product.image_url}`} alt={item.product.title} className="w-16 h-16 object-cover rounded" onError={(e) => { e.target.src = '/assets/8.jpg'; }} />
                        <div>
                          <p className="font-medium">{item.product.title}</p>
                          <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                        </div>
                      </div>
                      <span className="font-semibold">₹{item.product.price * item.quantity}</span>
                    </li>
                  ))}
                </ul>
                <div className="flex justify-between text-xl font-bold mb-6">
                  <span>Total</span>
                  <span>₹{subtotal}</span>
                </div>
                <button onClick={() => setStep(2)} className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                  Proceed to Shipping
                </button>
              </>
            )}
          </div>
        )}

        {step === 2 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Shipping */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold mb-4">Shipping Details</h2>
              <div className="space-y-3">
                <input name="name" value={guestInfo.name} onChange={handleGuestChange} placeholder="Full Name" className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-400 outline-none" />
                <input name="email" type="email" value={guestInfo.email} onChange={handleGuestChange} placeholder="Email" className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-400 outline-none" />
                <input name="mobile" value={guestInfo.mobile} onChange={handleGuestChange} placeholder="Mobile (10 digits)" className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-400 outline-none" />
                <textarea name="address" value={guestInfo.address} onChange={handleGuestChange} placeholder="Full Address" rows={3} className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-400 outline-none" />
              </div>

              <h3 className="text-lg font-semibold mt-6 mb-3">Payment Method</h3>
              <div className="space-y-2">
                {paymentMethods.map((m) => (
                  <label key={m.id} className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition ${paymentMethod === m.id ? "border-teal-500 bg-teal-50" : "hover:bg-gray-50"}`}>
                    <input type="radio" name="payment" value={m.id} checked={paymentMethod === m.id} onChange={() => setPaymentMethod(m.id)} />
                    <span className="text-xl">{m.icon}</span>
                    <span className="text-sm font-medium">{m.label}</span>
                  </label>
                ))}
              </div>

              <div className="flex gap-3 mt-6">
                <button onClick={() => setStep(1)} className="flex-1 border border-gray-300 py-2 rounded-lg hover:bg-gray-50">Back</button>
                <button onClick={handlePlaceOrder} disabled={processing} className="flex-1 bg-teal-600 text-white py-2 rounded-lg hover:bg-teal-700 transition disabled:opacity-50">
                  {processing ? "Processing..." : "Place Order"}
                </button>
              </div>
            </div>

            {/* Order summary side */}
            <div className="bg-white rounded-xl shadow-sm p-6 h-fit space-y-4">
              <h2 className="text-xl font-semibold mb-4">Order Total</h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span>Subtotal</span><span>₹{subtotal.toFixed(2)}</span></div>
                <div className="flex justify-between"><span>Shipping</span><span className="text-green-600">Free</span></div>
                <div className="flex justify-between"><span>Tax</span><span>₹{tax.toFixed(2)}</span></div>
                {discount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Discount</span>
                    <span>-₹{discount.toFixed(2)}</span>
                  </div>
                )}
                <div className="border-t pt-2 flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span>₹{total.toFixed(2)}</span>
                </div>
              </div>

              {/* Coupon Input */}
              <div className="border-t pt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Promo Code</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    placeholder="Enter code"
                    className="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-teal-400 outline-none"
                  />
                  <button
                    onClick={handleApplyCoupon}
                    disabled={couponLoading}
                    className="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-900 transition disabled:opacity-50"
                  >
                    {couponLoading ? "..." : "Apply"}
                  </button>
                </div>
                {couponData?.valid && (
                  <p className="text-xs text-green-600 mt-1">{couponData.message}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {step === 3 && placedOrder && (
          <motion.div
            className="bg-white rounded-xl shadow-sm p-10 text-center"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
          >
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-3xl font-bold text-gray-800 mb-2">Order Placed Successfully!</h2>
            <p className="text-gray-500 mb-2">Thank you for your purchase. A confirmation email has been sent.</p>
            <p className="text-lg font-semibold text-teal-700 mb-6">Order ID: #{placedOrder.id}</p>
            <div className="flex justify-center gap-4">
              <button onClick={() => navigate("/orders")} className="bg-gray-800 text-white px-6 py-3 rounded-lg hover:bg-gray-900 transition">
                Track Order
              </button>
              <button onClick={() => navigate("/")} className="bg-teal-600 text-white px-8 py-3 rounded-lg hover:bg-teal-700 transition">
                Continue Shopping
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

