import React, { useState, useEffect } from "react";

/* ---------- high‑quality electronics product images (optimised for carousel) ---------- */
const slides = [
  {
    image:
      "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=1200&h=600&fit=crop&q=80",
    title: "Latest Laptop Model",
    description:
      "Powerful performance in a sleek, portable design.",
  },
  {
    image:
      "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=1200&h=600&fit=crop&q=80",
    title: "Smartphone Pro",
    description:
      "Pro-grade camera and all‑day battery.",
  },
  {
    image:
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1200&h=600&fit=crop&q=80",
    title: "Wireless Headphones",
    description:
      "Immersive audio with ANC.",
  },
  {
    image:
      "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=1200&h=600&fit=crop&q=80",
    title: "DSLR Camera",
    description:
      "Stunning clarity for every shot.",
  },
  {
    image:
      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1200&h=600&fit=crop&q=80",
    title: "Smartwatch Series",
    description:
      "Health & style on your wrist.",
  },
];

/* ---------- custom animation keyframes ---------- */
const style = `
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  .animate-fadeInUp {
    animation: fadeInUp 0.6s ease-out;
  }
`;

const CarouselWithCaptions = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  /* ---- autoplay ---- */
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) =>
        prev === slides.length - 1 ? 0 : prev + 1
      );
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const goToSlide = (index) => setCurrentIndex(index);
  const nextSlide = () =>
    setCurrentIndex((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
  const prevSlide = () =>
    setCurrentIndex((prev) => (prev === 0 ? slides.length - 1 : prev - 1));

  return (
    <>
      {/* inject keyframes */}
      <style>{style}</style>

      <div className="relative w-screen mx-auto overflow-hidden">
        {/* Slides container */}
        <div
          className="flex transition-transform duration-700 ease-in-out"
          style={{ transform: `translateX(-${currentIndex * 100}%)` }}
        >
          {slides.map((slide, index) => (
            <div
              key={index}
              className="w-screen flex-shrink-0 relative h-[600px]"
            >
              <img
                src={slide.image}
                alt={`Slide ${index + 1}`}
                className="w-full h-[600px] object-cover"
                loading="lazy"
              />

              {/* Caption – remounts on slide change for animation replay */}
              {index === currentIndex && (
                <div
                  key={`caption-${currentIndex}`}
                  className="absolute bottom-0 bg-black bg-opacity-50 text-white p-4 w-full text-center hidden md:block animate-fadeInUp"
                >
                  <h5 className="text-xl font-semibold">{slide.title}</h5>
                  <p className="text-sm">{slide.description}</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Indicators – added pulse effect on active dot */}
        <div className="absolute bottom-5 left-1/2 transform -translate-x-1/2 flex gap-2 z-10">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`h-3 w-3 rounded-full transition-all duration-300 ${
                index === currentIndex
                  ? "bg-white scale-125 animate-pulse"
                  : "bg-gray-400 hover:bg-gray-200"
              }`}
            />
          ))}
        </div>

        {/* Navigation buttons – with hover scale and shadow */}
        <button
          onClick={prevSlide}
          className="absolute top-1/2 left-4 transform -translate-y-1/2 bg-black bg-opacity-50 text-white px-3 py-2 rounded-full z-10 hover:bg-opacity-80 hover:scale-110 transition-all duration-300"
          aria-label="Previous slide"
        >
          ‹
        </button>
        <button
          onClick={nextSlide}
          className="absolute top-1/2 right-4 transform -translate-y-1/2 bg-black bg-opacity-50 text-white px-3 py-2 rounded-full z-10 hover:bg-opacity-80 hover:scale-110 transition-all duration-300"
          aria-label="Next slide"
        >
          ›
        </button>
      </div>
    </>
  );
};

export default CarouselWithCaptions;