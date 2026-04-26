import img21 from '../assets/21.jpg';
import img22 from '../assets/22.jpg';
import img23 from '../assets/23.jpg';
import img24 from '../assets/24.jpg';
import img25 from '../assets/25.jpg';
import img26 from '../assets/26.jpg';
import img27 from '../assets/27.jpg';
import img28 from '../assets/28.jpg';

const products = [
  {
    id: 1,
    title: "Wireless Headphones",
    description: "Premium wireless headphones with noise cancellation and 20-hour battery life.",
    image: img21,
    category: "Most Selling",
    price: 3999
  },
  {
    id: 2,
    title: "Smart Watch",
    description: "Stay connected and track your health with this advanced smart watch.",
    image: img22,
    category: "Trending",
    price: 2999
  },
  {
    id: 3,
    title: "Bluetooth Speaker",
    description: "Compact and waterproof speaker with deep bass and long battery life.",
    image: img23,
    category: "Regular",
    price: 1499
  },
  {
    id: 4,
    title: "DSLR Camera",
    description: "Professional-quality DSLR camera for stunning photography and video.",
    image: img24,
    category: "Most Selling",
    price: 25999
  },
  {
    id: 5,
    title: "Gaming Mouse",
    description: "High-precision gaming mouse with customizable buttons and RGB lighting.",
    image: img25,
    category: "Trending",
    price: 999
  },
  {
    id: 6,
    title: "Mechanical Keyboard",
    description: "Durable mechanical keyboard with tactile feedback and backlit keys.",
    image: img26,
    category: "Regular",
    price: 2199
  },
  {
    id: 7,
    title: "4K Monitor",
    description: "Ultra HD 4K monitor with vibrant colors and sharp display for professionals.",
    image: img27,
    category: "Most Selling",
    price: 19999
  },
  {
    id: 8,
    title: "Noise Cancelling Earbuds",
    description: "Compact earbuds with active noise cancelling and long battery life.",
    image: img28,
    category: "Trending",
    price: 1799
  }
];

const categoryColor = {
  "Most Selling": "bg-rose-100 text-rose-700",
  "Trending": "bg-yellow-100 text-yellow-700",
  "Regular": "bg-gray-100 text-gray-800",
};
