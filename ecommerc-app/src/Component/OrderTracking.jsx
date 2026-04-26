import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { getMyOrders, getOrder } from "../services/api";

const STATUS_STEPS = ["pending", "confirmed", "shipped", "delivered"];

export default function OrderTracking() {
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const data = await getMyOrders();
      setOrders(data);
    } catch (err) {
      setError(err.message || "Failed to load orders");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOrder = async (orderId) => {
    try {
      const data = await getOrder(orderId);
      setSelectedOrder(data);
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) return <div className="pt-24 text-center">Loading your orders...</div>;
  if (error) return <div className="pt-24 text-center text-red-500">{error}</div>;

  return (
    <motion.div
      className="min-h-screen bg-gray-50 pt-20 pb-10 px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">My Orders</h1>

        {orders.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-10 text-center text-gray-500">
            <p className="text-lg mb-2">No orders yet</p>
            <p className="text-sm">Once you place an order, it will appear here.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div
                key={order.id}
                className="bg-white rounded-xl shadow-sm p-5 cursor-pointer hover:shadow-md transition"
                onClick={() => handleSelectOrder(order.id)}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <p className="font-semibold text-gray-800">Order #{order.id}</p>
                    <p className="text-sm text-gray-500">{new Date(order.created_at).toLocaleDateString()} · {order.item_count} items</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${statusBadge(order.status)}`}>
                      {order.status}
                    </span>
                    <span className="font-bold text-gray-800">₹{Number(order.total).toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Order Detail Modal */}
        {selectedOrder && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <motion.div
              className="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
            >
              <div className="p-6 border-b flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-800">Order #{selectedOrder.id}</h2>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="p-6 space-y-6">
                {/* Status Timeline */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">Order Status</h3>
                  <div className="flex items-center">
                    {STATUS_STEPS.map((step, idx) => {
                      const currentIdx = STATUS_STEPS.indexOf(selectedOrder.status);
                      const isActive = idx <= currentIdx;
                      const isLast = idx === STATUS_STEPS.length - 1;
                      return (
                        <React.Fragment key={step}>
                          <div className="flex flex-col items-center">
                            <div
                              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                                isActive ? "bg-teal-600 text-white" : "bg-gray-200 text-gray-500"
                              }`}
                            >
                              {idx + 1}
                            </div>
                            <span className={`text-xs mt-1 capitalize ${isActive ? "text-teal-700 font-medium" : "text-gray-400"}`}>
                              {step}
                            </span>
                          </div>
                          {!isLast && (
                            <div className={`flex-1 h-1 mx-2 ${isActive && idx < currentIdx ? "bg-teal-600" : "bg-gray-200"}`} />
                          )}
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>

                {/* Items */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">Items</h3>
                  <ul className="space-y-3">
                    {selectedOrder.items?.map((item) => (
                      <li key={item.id} className="flex justify-between items-center border-b pb-2">
                        <div>
                          <p className="font-medium text-gray-800">{item.product?.title || `Product #${item.product_id}`}</p>
                          <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                        </div>
                        <span className="font-medium">₹{(item.unit_price * item.quantity).toFixed(2)}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Totals */}
                <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Subtotal</span>
                    <span>₹{Number(selectedOrder.subtotal).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tax</span>
                    <span>₹{Number(selectedOrder.tax).toFixed(2)}</span>
                  </div>
                  {selectedOrder.discount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount</span>
                      <span>-₹{Number(selectedOrder.discount).toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between font-bold text-base pt-2 border-t">
                    <span>Total</span>
                    <span>₹{Number(selectedOrder.total).toFixed(2)}</span>
                  </div>
                </div>

                {selectedOrder.coupon_code && (
                  <p className="text-sm text-teal-600 font-medium">Coupon applied: {selectedOrder.coupon_code}</p>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function statusBadge(status) {
  switch (status) {
    case "delivered": return "bg-green-100 text-green-700";
    case "shipped": return "bg-blue-100 text-blue-700";
    case "confirmed": return "bg-teal-100 text-teal-700";
    case "pending": return "bg-yellow-100 text-yellow-700";
    case "cancelled": return "bg-red-100 text-red-700";
    default: return "bg-gray-100 text-gray-700";
  }
}

