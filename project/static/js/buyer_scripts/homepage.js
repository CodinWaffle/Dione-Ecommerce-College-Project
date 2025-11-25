const productBuckets = window.__PRODUCT_BUCKETS__ || {};
const featuredProducts = Array.isArray(productBuckets.featured)
  ? productBuckets.featured
  : [];
const trendingProducts = Array.isArray(productBuckets.trending)
  ? productBuckets.trending
  : [];
const newArrivals = Array.isArray(
  productBuckets.new_arrivals || productBuckets.newArrivals
)
  ? productBuckets.new_arrivals || productBuckets.newArrivals
  : [];

function normalizeProduct(product) {
  if (!product) return null;
  return {
    id: product.id || `product-${Math.random().toString(36).slice(2)}`,
    name: product.name || "New Product",
    primaryImage: product.primaryImage || "/static/image/banner.png",
    secondaryImage:
      product.secondaryImage ||
      product.primaryImage ||
      "/static/image/banner.png",
    material: product.material || "Premium Material",
    price: Number(product.price) || 0,
    originalPrice: Number(product.originalPrice) || 0,
  };
}

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

document.addEventListener("DOMContentLoaded", () => {
  if (typeof initializeProducts === "function") {
    [
      ["featured-products", featuredProducts],
      ["trending-products", trendingProducts],
      ["new-arrivals", newArrivals],
    ].forEach(([containerId, items]) => {
      const prepared = (items || [])
        .map((item) => normalizeProduct(item))
        .filter(Boolean);
      if (prepared.length) {
        initializeProducts(containerId, prepared);
      }
    });
  }

  const wishlistButtons = document.querySelectorAll(".wishlist-btn");
  wishlistButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const isFilled = btn.textContent === "?T?";
      btn.textContent = isFilled ? "?T?" : "?T?";
      btn.style.color = isFilled ? "inherit" : "var(--primary-color)";
    });
  });

  const addToCartButtons = document.querySelectorAll(".btn-outline");
  addToCartButtons.forEach((btn) => {
    if (btn.textContent.includes("Add to Cart")) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const originalText = btn.textContent;
        btn.textContent = "Added!";
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
