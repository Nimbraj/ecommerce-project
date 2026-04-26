// src/App.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './Component/header';
import First from './First';
import Login from './Component/Login';
import RegisterForm from './Component/rester';
import About from './About';
import Product from './Product';
import Cart from './Card';
import ProductDetail from './Component/ProductDetail';
import Checkout from './Component/Checkout';
import Wishlist from './Component/Wishlist';
import OrderTracking from './Component/OrderTracking';
import AdminDashboard from './Component/AdminDashboard';

export default function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<First />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route path="/about" element={<About />} />
        <Route path="/product" element={<Product/>} />
        <Route path="/product/:id" element={<ProductDetail />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/wishlist" element={<Wishlist />} />
        <Route path="/orders" element={<OrderTracking />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </>
  );
}
