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

    // Set image with fallback
    const image = this.element.querySelector(".product-image");
    // Prefer normalized primaryImage; if it's a relative uploads path, ensure it is reachable
    let primarySrc =
      this.product.primaryImage ||
      this.product.primary_image ||
      "/static/image/banner.png";
    let secondarySrc =
      this.product.secondaryImage || this.product.secondary_image || "";

    image.src = primarySrc;
    image.alt = this.product.name;

    // Add error handling for broken images
    image.onerror = function () {
      this.src = "/static/image/banner.png";
    };

    // Attach hover swap to show secondary image on hover (if available)
    try {
      if (secondarySrc) {
        image.dataset.secondary = secondarySrc;
        const cardRoot = this.element.querySelector(".product-card");
        if (cardRoot) {
          cardRoot.addEventListener("mouseenter", function () {
            try {
              if (image.dataset && image.dataset.secondary)
                image.src = image.dataset.secondary;
            } catch (e) {}
          });
          cardRoot.addEventListener("mouseleave", function () {
            try {
              image.src = primarySrc;
            } catch (e) {}
          });
        }
      }
    } catch (e) {
      // ignore hover enhancements if DOM doesn't support
    }

    // Set product info
    this.element.querySelector(".product-name").textContent = this.product.name;

    // Set rating if present
    const ratingEl = this.element.querySelector(".rating-value");
    if (ratingEl) {
      if (this.product.rating != null) {
        const rating = parseFloat(this.product.rating).toFixed(1);
        const reviewCount =
          this.product.reviewCount || Math.floor(Math.random() * 100) + 10;
        ratingEl.textContent = `${rating} (${reviewCount})`;
      } else {
        ratingEl.textContent = "4.4 (42)";
      }
    }

    // Set price
    const priceContainer =
      this.element.querySelector(".product-price") ||
      this.element.querySelector(".price-container");
    const currentPriceSpan = priceContainer.querySelector(".current-price");
    const originalPriceSpan = priceContainer.querySelector(".original-price");
    const discountBadge = priceContainer.querySelector(".discount-badge");

    currentPriceSpan.textContent = `₱${this.product.price.toLocaleString()}`;

    if (
      this.product.originalPrice &&
      this.product.originalPrice > this.product.price
    ) {
      originalPriceSpan.textContent = `₱${this.product.originalPrice.toLocaleString()}`;
      originalPriceSpan.style.display = "inline";

      // Calculate and show discount
      const discount = Math.round(
        ((this.product.originalPrice - this.product.price) /
          this.product.originalPrice) *
          100
      );
      if (discountBadge && discount > 0) {
        discountBadge.textContent = `-${discount}%`;
        discountBadge.style.display = "inline";
      }
    } else {
      if (originalPriceSpan) originalPriceSpan.style.display = "none";
      if (discountBadge) discountBadge.style.display = "none";
    }

    // Add click listener to navigate to product detail page
    const productCard = this.element.querySelector(".product-card");
    if (productCard) {
      productCard.addEventListener("click", (e) => this.handleCardClick(e));
      // Make card keyboard accessible
      try {
        productCard.setAttribute("role", "link");
        productCard.tabIndex = 0;
        productCard.addEventListener("keydown", (e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            this.handleCardClick(e);
          }
        });
      } catch (err) {
        // ignore environments that don't allow setting these
      }
    }

    // Add button listeners
    const wishlistBtn = this.element.querySelector(".wishlist-btn");
    if (wishlistBtn) {
      wishlistBtn.addEventListener("click", (e) =>
        this.handleWishlist(e, wishlistBtn)
      );
    }

    return this.element;
  }

  handleHoverStart(productCard) {
    productCard.classList.add("hovered");
  }

  handleHoverEnd(productCard) {
    productCard.classList.remove("hovered");
  }

  handleCardClick(e) {
    // Don't navigate if clicking on action buttons
    if (e.target.closest(".action-button") || e.target.closest(".action-btn")) {
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
      `initializeProducts: id=${product.id}, name=${
        product.name
      }, primaryImage=${product.primaryImage}, secondaryImage=${
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
