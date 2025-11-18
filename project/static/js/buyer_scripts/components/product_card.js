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
    const card = new ProductCard(product, template);
    const cardElement = card.render();
    productGrid.appendChild(cardElement);
  });
}

// Expose for global use
window.ProductCard = ProductCard;
window.initializeProducts = initializeProducts;
