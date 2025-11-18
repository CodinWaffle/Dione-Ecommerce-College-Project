// Sample Products Data
const featuredProducts = [
  {
    id: "product-1",
    name: "Summer White Tee",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Sustainable Cotton",
    price: 4999,
    originalPrice: 5999,
  },
  {
    id: "product-2",
    name: "Premium Denim Jacket",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Eco-Friendly Denim",
    price: 12999,
    originalPrice: 15999,
  },
  {
    id: "product-3",
    name: "Linen Pants",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Natural Fibers",
    price: 8999,
    originalPrice: 10999,
  },
  {
    id: "product-4",
    name: "Silk Blouse",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Premium Silk",
    price: 9999,
    originalPrice: 12999,
  },
  {
    id: "product-5",
    name: "Oversized Sweater",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Organic Wool",
    price: 11999,
    originalPrice: 14999,
  },
];

const trendingProducts = [
  {
    id: "product-6",
    name: "Cropped Pink Top",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "This Season's Color",
    price: 3999,
    originalPrice: 5999,
  },
  {
    id: "product-7",
    name: "Oversized Blazer",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Modern Classic",
    price: 13999,
    originalPrice: 17999,
  },
  {
    id: "product-8",
    name: "Black Cargo Pants",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Functional Fashion",
    price: 8499,
    originalPrice: 10499,
  },
  {
    id: "product-9",
    name: "Striped Dress",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Versatile Essential",
    price: 7499,
    originalPrice: 9499,
  },
  {
    id: "product-10",
    name: "Vegan Leather Jacket",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Eco Alternative",
    price: 14999,
    originalPrice: 18999,
  },
];

const newArrivals = [
  {
    id: "product-11",
    name: "Minimalist Cardigan",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Fresh This Week",
    price: 9499,
    originalPrice: 11999,
  },
  {
    id: "product-12",
    name: "Maxi Skirt",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Fresh This Week",
    price: 7999,
    originalPrice: 9999,
  },
  {
    id: "product-13",
    name: "Crop Tank Top",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Fresh This Week",
    price: 3499,
    originalPrice: 4999,
  },
  {
    id: "product-14",
    name: "Wide Leg Trousers",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Fresh This Week",
    price: 9999,
    originalPrice: 12499,
  },
  {
    id: "product-15",
    name: "Linen Shirt",
    primaryImage: "/placeholder.svg?height=300&width=250",
    secondaryImage: "/placeholder.svg?height=300&width=250",
    material: "Fresh This Week",
    price: 6999,
    originalPrice: 8999,
  },
];

// Carousel scroll functionality
function scrollCarousel(button, direction) {
  const carousel = button
    .closest(".carousel-container")
    .querySelector(".carousel");
  const cardWidth = carousel.querySelector(".product-card").offsetWidth + 32;

  if (direction === -1) {
    carousel.scrollBy({ left: -cardWidth, behavior: "smooth" });
  } else {
    carousel.scrollBy({ left: cardWidth, behavior: "smooth" });
  }
}

// Initialize products on page load
document.addEventListener("DOMContentLoaded", () => {
  // Initialize product grids with the ProductCard class
  if (typeof initializeProducts === "function") {
    initializeProducts("featured-products", featuredProducts);
    initializeProducts("trending-products", trendingProducts);
    initializeProducts("new-arrivals", newArrivals);
  }

  // Wishlist toggle
  const wishlistButtons = document.querySelectorAll(".wishlist-btn");

  wishlistButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const isFilled = btn.textContent === "♥";
      btn.textContent = isFilled ? "♡" : "♥";
      btn.style.color = isFilled ? "inherit" : "var(--primary-color)";
    });
  });

  // Add to cart handlers
  const addToCartButtons = document.querySelectorAll(".btn-outline");

  addToCartButtons.forEach((btn) => {
    if (btn.textContent.includes("Add to Cart")) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const originalText = btn.textContent;
        btn.textContent = "✓ Added!";
        btn.style.backgroundColor = "var(--primary-color)";
        btn.style.color = "white";

        setTimeout(() => {
          btn.textContent = originalText;
          btn.style.backgroundColor = "";
          btn.style.color = "";
        }, 2000);
      });
    }
  });
});
