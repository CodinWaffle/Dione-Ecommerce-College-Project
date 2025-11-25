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

    // Set images
    const images = this.element.querySelectorAll(".product-image");
    images[0].src = this.product.primaryImage;
    images[0].alt = `${this.product.name} - Front`;
    images[1].src = this.product.secondaryImage;
    images[1].alt = `${this.product.name} - Back`;

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
    // Navigate to product detail page
    window.location.href = `/product/${this.product.id}`;
  }

  handleWishlist(e, button) {
    e.stopPropagation();
    this.isWishlisted = !this.isWishlisted;
    button.classList.toggle("active");
  }

  handleAddToCart(e) {
    e.stopPropagation();
    alert(`Added "${this.product.name}" to cart`);
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
      `initializeProducts: id=${product.id}, secondaryImage=${
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
