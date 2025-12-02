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

    // Set sold count
    const soldEl = this.element.querySelector(".sold-count");
    if (soldEl) {
      const soldCount = this.product.soldCount || this.product.sold_count || 0;
      soldEl.textContent = `${soldCount} sold`;
    }

    // Set colors/variants
    this.renderColorVariants();

    // Set price
    const priceContainer = this.element.querySelector(".product-price");
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
    const cartBtn = this.element.querySelector(".cart-btn");
    if (cartBtn) {
      cartBtn.addEventListener("click", (e) => this.handleAddToCart(e));
    }

    const buyNowBtn = this.element.querySelector(".buy-now-btn");
    if (buyNowBtn) {
      buyNowBtn.addEventListener("click", (e) => this.handleBuyNow(e));
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

  renderColorVariants() {
    const colorsContainer = this.element.querySelector(".product-colors");
    if (!colorsContainer) {
      console.warn("Colors container not found");
      return;
    }

    // Clear existing colors
    colorsContainer.innerHTML = "";

    // Get variants from product data
    const variants = this.product.variants || [];
    console.log(`Product ${this.product.name} variants:`, variants);

    // Always show the colors container, even if empty
    colorsContainer.style.display = "flex";

    if (variants.length === 0) {
      console.log(`No variants found for product ${this.product.name}, showing default`);
      // If no variants specified, show a default color indicator
      const defaultColorDot = document.createElement("div");
      defaultColorDot.className = "color-dot";
      defaultColorDot.style.backgroundColor = "#e5e7eb";
      defaultColorDot.style.cursor = "default";
      
      const tooltip = document.createElement("span");
      tooltip.className = "color-tooltip";
      tooltip.textContent = "Default";
      defaultColorDot.appendChild(tooltip);
      
      colorsContainer.appendChild(defaultColorDot);
      return;
    }

    console.log(`Rendering ${variants.length} color variants for ${this.product.name}`);
    variants.slice(0, 5).forEach((variant, index) => {
      const colorDot = document.createElement("button");
      colorDot.className = `color-dot`;
      
      // Use actual color hex from database if available, otherwise fallback to color mapping
      const colorHex = variant.colorHex || this.getColorValue(variant.color);
      console.log(`Variant ${index}: ${variant.color} -> ${colorHex}`);
      
      colorDot.style.backgroundColor = colorHex;
      colorDot.setAttribute("aria-label", `Select ${variant.color} variant`);
      colorDot.dataset.variantIndex = index;
      
      // Create tooltip
      const tooltip = document.createElement("span");
      tooltip.className = "color-tooltip";
      tooltip.textContent = variant.color;
      colorDot.appendChild(tooltip);
      
      // Add click handler to change product image
      colorDot.addEventListener("click", (e) => {
        e.stopPropagation();
        this.handleColorSelect(variant, colorDot);
      });

      if (index === 0) {
        colorDot.classList.add("active");
      }

      colorsContainer.appendChild(colorDot);
    });
  }

  getColorValue(colorName) {
    const colorMap = {
      red: "#ef4444",
      blue: "#3b82f6", 
      green: "#10b981",
      black: "#000000",
      white: "#ffffff",
      purple: "#8b5cf6",
      pink: "#ec4899",
      yellow: "#f59e0b",
      orange: "#f97316",
      gray: "#6b7280",
      grey: "#6b7280",
      brown: "#92400e",
      navy: "#1e3a8a",
      teal: "#14b8a6",
      lime: "#84cc16",
      indigo: "#6366f1",
      violet: "#8b5cf6",
      rose: "#f43f5e",
      emerald: "#10b981",
      sky: "#0ea5e9",
      amber: "#f59e0b",
      slate: "#64748b",
      zinc: "#71717a",
      neutral: "#737373",
      stone: "#78716c",
      cyan: "#06b6d4",
      fuchsia: "#d946ef"
    };
    return colorMap[colorName.toLowerCase()] || colorName;
  }

  handleColorSelect(variant, colorDot) {
    // Remove active class from all color dots
    this.element.querySelectorAll(".color-dot").forEach(dot => {
      dot.classList.remove("active");
    });
    
    // Add active class to selected dot
    colorDot.classList.add("active");

    // Update images to show variant-specific images
    const primaryImage = this.element.querySelector(".primary-image");
    const secondaryImage = this.element.querySelector(".secondary-image");
    
    if (variant && variant.image) {
      // Update primary image to variant image
      primaryImage.src = variant.image;
      
      // Update secondary image if variant has one, otherwise use variant image
      if (variant.secondaryImage) {
        secondaryImage.src = variant.secondaryImage;
      } else {
        // Use variant image as secondary or keep original secondary
        const originalSecondary = this.product.secondaryImage || this.product.secondary_image;
        secondaryImage.src = originalSecondary || variant.image;
      }
    }
  }

  handleBuyNow(e) {
    e.stopPropagation();
    e.preventDefault();

    // Get selected color
    const activeColorDot = this.element.querySelector(".color-dot.active");
    const selectedColor = activeColorDot ? activeColorDot.getAttribute("aria-label").replace("Select ", "").replace(" variant", "") : "";

    // Navigate to product detail page with buy now intent
    const url = `/product/${this.product.id}?buyNow=true${selectedColor ? `&color=${encodeURIComponent(selectedColor)}` : ""}`;
    window.location.href = url;
  }

  handleAddToCart(e) {
    // Prevent the card click navigation and other propagation
    e.stopPropagation();
    e.preventDefault();

    // Get selected color from active color dot
    const activeColorDot = this.element.querySelector(".color-dot.active");
    const selectedColor = activeColorDot ? 
      activeColorDot.getAttribute("aria-label").replace("Select ", "").replace(" variant", "") : 
      (this.product.color || "");

    // Default quantity and size (cards add one item with default size)
    const qty = 1;
    const size = this.product.size || "One Size";

    // Get variant image if available
    const selectedVariant = this.product.variants?.find(v => v.color === selectedColor);
    const variantImage = selectedVariant?.image || this.product.primaryImage;

    // Prepare cart data
    const cartData = {
      product_id: this.product.id,
      color: selectedColor,
      size: size,
      quantity: qty
    };

    // Call add to cart API directly
    fetch("/add-to-cart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cartData),
    })
    .then(response => response.json())
    .then(data => {
      if (data && data.success) {
        // Prepare data for cart modal
        const modalData = {
          name: this.product.name,
          price: this.product.price,
          color: selectedColor,
          size: size,
          quantity: qty,
          image: variantImage,
          sellerId: this.product.sellerId || this.product.seller_id,
          productId: this.product.id
        };

        // Update cart count
        if (typeof updateCartCount === "function" && data.cart_count !== undefined) {
          updateCartCount(data.cart_count);
        }

        // Populate and show cart modal
        if (typeof window.populateCartModal === "function") {
          window.populateCartModal(modalData);
        }

        // Show success animation then modal
        if (typeof showCartSuccessAnimation === "function") {
          showCartSuccessAnimation();
        } else if (typeof openCartModal === "function") {
          openCartModal();
        }

        // Visual feedback on the button
        const btn = e.currentTarget;
        if (btn) {
          btn.classList.add("added");
          setTimeout(() => btn.classList.remove("added"), 700);
        }
      } else {
        console.error("Add to cart failed:", data.error);
        alert("Failed to add item to cart. Please try again.");
      }
    })
    .catch(error => {
      console.error("Error adding to cart:", error);
      alert("Failed to add item to cart. Please try again.");
    });
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
