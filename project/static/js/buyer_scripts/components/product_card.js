// Product Card Class
class ProductCard {
  constructor(product, template) {
    this.product = product;
    this.template = template;
    this.isWishlisted = false;
    this.element = null;
  }

  render() {
    // Clone the template
    this.element = this.template.content.cloneNode(true);

    // Set images with fallbacks
    const images = this.element.querySelectorAll(".product-image");
    images[0].src = this.product.primaryImage || '/static/image/banner.png';
    images[0].alt = `${this.product.name} - Front`;
    images[1].src = this.product.secondaryImage || this.product.primaryImage || '/static/image/banner.png';
    images[1].alt = `${this.product.name} - Back`;
    
    // Add error handling for broken images
    images[0].onerror = function() {
      this.src = '/static/image/banner.png';
    };
    images[1].onerror = function() {
      this.src = '/static/image/banner.png';
    };

    // Set product info
    this.element.querySelector(".product-name").textContent = this.product.name;
    this.element.querySelector(".material-badge").textContent =
      this.product.material;

    // Set rating if present
    const ratingEl = this.element.querySelector(".rating-value");
    if (ratingEl) {
      if (this.product.rating != null) {
        // Show star and numeric value
        ratingEl.textContent = `⭐ ${parseFloat(this.product.rating).toFixed(
          1
        )}`;
      } else {
        ratingEl.textContent = "";
      }
    }

    // Set price
    const priceContainer = this.element.querySelector(".price-container");
    const currentPriceSpan = priceContainer.querySelector(".current-price");
    const originalPriceSpan = priceContainer.querySelector(".original-price");

    currentPriceSpan.textContent = `₱${this.product.price.toLocaleString()}`;

    if (this.product.originalPrice) {
      originalPriceSpan.textContent = `₱${this.product.originalPrice.toLocaleString()}`;
    } else {
      originalPriceSpan.remove();
    }

    // Get the card wrapper element
    const cardWrapper = this.element.querySelector(".card-wrapper");

    // Add hover listeners
    cardWrapper.addEventListener("mouseenter", () =>
      this.handleHoverStart(cardWrapper)
    );
    cardWrapper.addEventListener("mouseleave", () =>
      this.handleHoverEnd(cardWrapper)
    );

    // Add click listener to navigate to product detail page
    const productCard = this.element.querySelector(".product-card");
    productCard.addEventListener("click", (e) => this.handleCardClick(e));

    // Add button listeners
    const wishlistBtn = this.element.querySelector(".wishlist-btn");
    const cartBtn = this.element.querySelector(".cart-btn");

    wishlistBtn.addEventListener("click", (e) =>
      this.handleWishlist(e, wishlistBtn)
    );
    cartBtn.addEventListener("click", (e) => this.handleAddToCart(e));

    return this.element;
  }

  handleHoverStart(cardWrapper) {
    cardWrapper.closest(".product-card").classList.add("hovered");
  }

  handleHoverEnd(cardWrapper) {
    cardWrapper.closest(".product-card").classList.remove("hovered");
  }

  handleCardClick(e) {
    // Don't navigate if clicking on action buttons
    if (e.target.closest(".action-button")) {
      return;
    }
    // If we're on a product detail page, fetch product JSON and populate the page
    const isDetail =
      document.querySelector(".product-details") ||
      document.getElementById("product-details") ||
      document.getElementById("mainImage");
    if (isDetail && window.fetch) {
      e.preventDefault();
      e.stopPropagation();
      const id = this.product.id;
      fetch(`/api/product/${id}`)
        .then((res) => {
          if (!res.ok) throw new Error("Fetch error");
          return res.json();
        })
        .then((json) => {
          if (json && json.product) {
            // populate detail view using global helper if available
            if (typeof window.populateProductDetail === "function") {
              window.populateProductDetail(json.product);
            } else {
              // fallback: navigate to detail page
              window.location.href = `/product/${id}`;
            }
          } else {
            window.location.href = `/product/${id}`;
          }
        })
        .catch((err) => {
          console.error("Error loading product detail", err);
          window.location.href = `/product/${this.product.id}`;
        });
      return;
    }

    // Default behavior: Navigate to product detail page
    window.location.href = `/product/${this.product.id}`;
  }

  handleWishlist(e, button) {
    e.stopPropagation();
    this.isWishlisted = !this.isWishlisted;
    button.classList.toggle("active");
  }

  handleAddToCart(e) {
    // Prevent the card click navigation and other propagation
    e.stopPropagation();
    e.preventDefault();

    // Default quantity (cards add one item)
    const qty = 1;
    const size = this.product.size || "";
    const color = this.product.color || "";

    // Use global addToBag (which calls addToCart + updates badge)
    if (typeof addToBag === "function") {
      addToBag(
        this.product.id,
        this.product.name,
        this.product.price,
        size,
        color,
        qty
      );
    } else if (typeof addToCart === "function") {
      // fallback: call addToCart directly
      addToCart(
        this.product.id,
        this.product.name,
        this.product.price,
        size,
        color,
        qty
      );
      // increment visible badge locally as fallback
      const current =
        parseInt(
          (document.querySelector(".cart-count") || { textContent: 0 })
            .textContent
        ) || 0;
      if (typeof updateCartCount === "function") updateCartCount(current + qty);
    } else {
      // Last resort: show native alert
      alert(`Added "${this.product.name}" to cart`);
      const current =
        parseInt(
          (document.querySelector(".cart-count") || { textContent: 0 })
            .textContent
        ) || 0;
      if (typeof updateCartCount === "function") updateCartCount(current + qty);
    }

    // Visual feedback on the button
    const btn = e.currentTarget;
    if (btn) {
      btn.classList.add("added");
      setTimeout(() => btn.classList.remove("added"), 700);
    }
  }
}

// Initialize Products
function initializeProducts(containerId, products) {
  const template = document.getElementById("productCardTemplate");
  const productGrid = document.getElementById(containerId);

  if (!productGrid) {
    console.warn(`Container with id "${containerId}" not found`);
    return;
  }

  products.forEach((product) => {
    console.log(
      `initializeProducts: id=${product.id}, name=${product.name}, primaryImage=${product.primaryImage}, secondaryImage=${
        product.secondaryImage ? "yes" : "no"
      }`
    );
    const card = new ProductCard(product, template);
    const cardElement = card.render();
    productGrid.appendChild(cardElement);
  });
}

// Expose for global use
window.ProductCard = ProductCard;
window.initializeProducts = initializeProducts;
