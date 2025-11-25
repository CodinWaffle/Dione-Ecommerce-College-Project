// Global variables
let currentImageIndex = 0;
const totalImages = 3;

// Image switching functionality
function changeMainImage(thumbnail, index) {
  const mainImage = document.getElementById("mainImage");
  const thumbnails = document.querySelectorAll(".thumbnail");

  // Update main image
  mainImage.src = thumbnail.src;

  // Update active thumbnail
  thumbnails.forEach((thumb) => thumb.classList.remove("active"));
  thumbnail.classList.add("active");

  // Update current index
  currentImageIndex = index;
}

document.addEventListener("DOMContentLoaded", () => {
  // Initialize stock display and availability
  updateSizeAvailability();
  updateColorAvailability();
  updateStockDisplay();

  // Initialize quantity buttons
  updateQuantityButtons();

  // Add event listeners to quantity buttons (in case onclick doesn't work)
  const decreaseBtn = document.getElementById("decreaseBtn");
  const increaseBtn = document.getElementById("increaseBtn");
  const quantityInput = document.getElementById("quantityInput");

  if (decreaseBtn) {
    decreaseBtn.addEventListener("click", decreaseQuantity);
  }

  if (increaseBtn) {
    increaseBtn.addEventListener("click", increaseQuantity);
  }

  if (quantityInput) {
    quantityInput.addEventListener("input", updateQuantity);
    quantityInput.addEventListener("change", updateQuantity);
  }
});

// Global variables for stock management
let currentSelectedColor = "Black";
let currentSelectedSize = "XS";

// Update stock display
function updateStockDisplay() {
  const stockIndicator = document.getElementById("stockIndicator");
  const activeColorBtn = document.querySelector(".color-option.active");
  const activeSizeBtn = document.querySelector(".size-option.active");

  if (activeColorBtn && activeSizeBtn) {
    const colorStock = JSON.parse(activeColorBtn.dataset.stock);
    const selectedSize = activeSizeBtn.dataset.size;
    const stock = colorStock[selectedSize];

    stockIndicator.textContent = stock > 0 ? stock : "0";

    // Update stock indicator styling
    stockIndicator.className = "stock-indicator";
    if (stock === 0) {
      stockIndicator.classList.add("out-of-stock");
    } else if (stock <= 3) {
      stockIndicator.classList.add("low-stock");
    } else {
      stockIndicator.classList.add("in-stock");
    }

    // Update add to bag button
    const addToBagBtn = document.querySelector(".add-to-bag-btn");
    if (stock === 0) {
      addToBagBtn.disabled = true;
      addToBagBtn.textContent = "OUT OF STOCK";
      addToBagBtn.style.opacity = "0.5";
      addToBagBtn.style.cursor = "not-allowed";
    } else {
      addToBagBtn.disabled = false;
      addToBagBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <path d="M16 10a4 4 0 0 1-8 0"></path>
        </svg>
        ADD TO BAG
      `;
      addToBagBtn.style.opacity = "1";
      addToBagBtn.style.cursor = "pointer";
    }

    // Update quantity buttons when stock changes
    updateQuantityButtons();
  }
}

// Update size availability based on color
function updateSizeAvailability() {
  const activeColorBtn = document.querySelector(".color-option.active");
  const sizeOptionsContainer = document.getElementById("sizeOptions");

  if (activeColorBtn && sizeOptionsContainer) {
    const colorStock = JSON.parse(activeColorBtn.dataset.stock);
    
    // Clear existing size options
    sizeOptionsContainer.innerHTML = '';
    
    // Create size options for the selected color
    let firstAvailableSize = null;
    Object.keys(colorStock).forEach((size, index) => {
      const stock = colorStock[size];
      const isAvailable = stock > 0;
      
      if (isAvailable && !firstAvailableSize) {
        firstAvailableSize = size;
      }
      
      const sizeBtn = document.createElement('button');
      sizeBtn.className = `size-option ${index === 0 && isAvailable ? 'active' : ''} ${!isAvailable ? 'disabled out-of-stock' : ''}`;
      sizeBtn.setAttribute('data-size', size);
      sizeBtn.setAttribute('data-stock', stock);
      sizeBtn.textContent = size;
      
      // Style the button
      sizeBtn.style.cssText = `
        padding: 8px 15px;
        border: 1px solid ${index === 0 && isAvailable ? '#8e44ad' : '#ddd'};
        border-radius: 4px;
        cursor: ${isAvailable ? 'pointer' : 'not-allowed'};
        background: ${index === 0 && isAvailable ? '#8e44ad' : 'white'};
        color: ${index === 0 && isAvailable ? 'white' : '#333'};
        margin-right: 10px;
        margin-bottom: 5px;
        ${!isAvailable ? 'opacity: 0.5; text-decoration: line-through;' : ''}
      `;
      
      if (isAvailable) {
        sizeBtn.onclick = () => selectSize(sizeBtn);
      }
      
      sizeOptionsContainer.appendChild(sizeBtn);
    });
    
    // Update current selected size
    if (firstAvailableSize) {
      currentSelectedSize = firstAvailableSize;
    }
  }
}

// Update color availability based on size
function updateColorAvailability() {
  const activeSizeBtn = document.querySelector(".size-option.active");
  const colorOptions = document.querySelectorAll(".color-option");

  if (activeSizeBtn) {
    const selectedSize = activeSizeBtn.dataset.size;

    colorOptions.forEach((colorBtn) => {
      const colorStock = JSON.parse(colorBtn.dataset.stock);
      const stock = colorStock[selectedSize];

      if (stock === 0) {
        colorBtn.classList.add("disabled");
        colorBtn.onclick = null;
      } else {
        colorBtn.classList.remove("disabled");
        colorBtn.onclick = () => selectColor(colorBtn);
      }
    });
  }
}

// Color selection
function selectColor(colorBtn) {
  // Don't allow selection of disabled colors
  if (colorBtn.classList.contains("disabled") || colorBtn.classList.contains("out-of-stock")) {
    return;
  }

  const colorOptions = document.querySelectorAll(".color-option");
  const selectedColorSpan = document.querySelector(".selected-color");

  colorOptions.forEach((option) => option.classList.remove("active"));
  colorBtn.classList.add("active");

  selectedColorSpan.textContent = colorBtn.dataset.color;
  currentSelectedColor = colorBtn.dataset.color;

  // Update size availability and stock display
  updateSizeAvailability();
  updateStockDisplay();

  // Swap main product image to variant image if available
  try {
    const colorKey = currentSelectedColor;
    const variantMap = window.variantPhotoMap || {};
    const variant = variantMap[colorKey];
    const mainImage = document.getElementById("mainImage");
    const zoomImage = document.getElementById("zoomImage");
    const thumbnails = document.querySelectorAll(".thumbnail");

    if (variant && mainImage) {
      // variant may be an object { primary: url, secondary: url } or a string
      const primary =
        typeof variant === "string"
          ? variant
          : variant.primary || variant.image || null;
      const secondary =
        typeof variant === "object" && variant.secondary
          ? variant.secondary
          : null;

      if (primary) {
        mainImage.src = primary;
        if (zoomImage) zoomImage.src = primary;
        // Update thumbnails to show variant images
        if (thumbnails && thumbnails.length > 0) {
          thumbnails.forEach((t, idx) => {
            if (idx === 0) {
              t.src = primary;
            } else if (idx === 1 && secondary) {
              t.src = secondary;
            } else if (idx > 1) {
              // Use primary image for additional thumbnails if no more variant images
              t.src = primary;
            }
          });
          // set first thumbnail active
          thumbnails.forEach((thumb) => thumb.classList.remove("active"));
          if (thumbnails[0]) thumbnails[0].classList.add("active");
        }
      }
    }
  } catch (err) {
    console.warn("Variant image swap failed", err);
  }
}

// Size selection
function selectSize(sizeBtn) {
  // Don't allow selection of disabled sizes
  if (sizeBtn.classList.contains("disabled") || sizeBtn.classList.contains("out-of-stock")) {
    return;
  }

  const sizeOptions = document.querySelectorAll(".size-option");

  sizeOptions.forEach((option) => {
    option.classList.remove("active");
    // Reset styling
    option.style.border = "1px solid #ddd";
    option.style.background = "white";
    option.style.color = "#333";
  });
  
  sizeBtn.classList.add("active");
  // Apply active styling
  sizeBtn.style.border = "1px solid #8e44ad";
  sizeBtn.style.background = "#8e44ad";
  sizeBtn.style.color = "white";

  currentSelectedSize = sizeBtn.dataset.size;

  // Update color availability and stock display
  updateColorAvailability();
  updateStockDisplay();
}

// Wishlist toggle
document.getElementById("wishlistBtn").addEventListener("click", function () {
  this.classList.toggle("active");
});

// Add to bag functionality
function addToBag() {
  const selectedColor = document.querySelector(".color-option.active").dataset
    .color;
  const selectedSize = document.querySelector(
    ".size-option.active"
  ).textContent;
  const selectedQuantity = document.getElementById("quantityInput").value;

  // Get product details from the page
  const productName = document.querySelector(".product-title").textContent;
  const productPrice = parseFloat(
    document.querySelector(".price").textContent.replace("$", "")
  );
  const productId =
    document.querySelector("[data-product-id]")?.dataset.productId ||
    Math.floor(Math.random() * 10000);

  // Update the popup with selected options
  updatePopupContent(selectedColor, selectedSize, selectedQuantity);

  // Add to cart using the cart.js function
  if (typeof addToCart === "function") {
    addToCart(
      productId,
      productName,
      productPrice,
      selectedSize,
      selectedColor,
      selectedQuantity
    );
  }

  // Show success animation first, then modal
  showCartSuccessAnimation();
}

// Function to update popup content dynamically
function updatePopupContent(color, size, quantity) {
  // Update size
  const modalSelectedSize = document.getElementById("cartModalSelectedSize");
  if (modalSelectedSize) {
    modalSelectedSize.textContent = size;
  }

  // Update color
  const modalSelectedColor = document.getElementById("cartModalSelectedColor");
  if (modalSelectedColor) {
    modalSelectedColor.textContent = color;
  }

  // Update quantity
  const modalSelectedQuantity = document.getElementById(
    "cartModalSelectedQuantity"
  );
  if (modalSelectedQuantity) {
    modalSelectedQuantity.textContent = quantity;
  }

  // Update product name to include color if needed
  const productNameElement = document.querySelector(
    ".cart-modal .cart-product-name"
  );
  if (productNameElement && color) {
    const baseName = productNameElement.textContent.split(" in ")[0]; // Remove existing color info
    productNameElement.textContent = `${baseName} in ${color}`;
  }

  // Update item count in header
  const itemCount = document.querySelector(".cart-item-count");
  if (itemCount) {
    const itemText = parseInt(quantity) === 1 ? "Item" : "Items";
    itemCount.textContent = `${quantity} ${itemText}`;
  }
}

// Expandable sections
function toggleSection(header) {
  const content = header.nextElementSibling;
  const isActive = header.classList.contains("active");

  // Close all sections
  document.querySelectorAll(".section-header").forEach((h) => {
    h.classList.remove("active");
    h.nextElementSibling.classList.remove("active");
  });

  // Open clicked section if it wasn't active
  if (!isActive) {
    header.classList.add("active");
    content.classList.add("active");
  }
}

// Bottom tabs functionality
function switchTab(tabBtn, tabId) {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach((btn) => btn.classList.remove("active"));
  tabPanels.forEach((panel) => panel.classList.remove("active"));

  tabBtn.classList.add("active");
  document.getElementById(tabId).classList.add("active");
}

// Breadcrumb navigation functions
function navigateToHome(event) {
  event.preventDefault();
  // Navigate to home page
  window.location.href = "/";
}

function navigateToCategory(event, category) {
  event.preventDefault();
  // Navigate to category page
  window.location.href = `/category/${category}`;
}

// Quantity management functions
function updateQuantityButtons() {
  const quantityInput = document.getElementById("quantityInput");
  const decreaseBtn = document.getElementById("decreaseBtn");
  const increaseBtn = document.getElementById("increaseBtn");
  const stockIndicator = document.getElementById("stockIndicator");

  const currentQuantity = parseInt(quantityInput.value) || 1;
  const availableStock = parseInt(stockIndicator.textContent) || 0;

  // Disable decrease button if quantity is 1
  decreaseBtn.disabled = currentQuantity <= 1;

  // Disable increase button if quantity equals available stock
  increaseBtn.disabled =
    currentQuantity >= availableStock || availableStock === 0;

  // Update max attribute of input
  quantityInput.max = availableStock;

  // Ensure quantity is within valid range
  if (currentQuantity > availableStock && availableStock > 0) {
    quantityInput.value = availableStock;
  } else if (currentQuantity < 1) {
    quantityInput.value = 1;
  }
}

function increaseQuantity() {
  const quantityInput = document.getElementById("quantityInput");
  const stockIndicator = document.getElementById("stockIndicator");

  const currentQuantity = parseInt(quantityInput.value) || 1;
  const availableStock = parseInt(stockIndicator.textContent) || 0;

  if (currentQuantity < availableStock) {
    quantityInput.value = currentQuantity + 1;
    updateQuantityButtons();
  }
}

function decreaseQuantity() {
  const quantityInput = document.getElementById("quantityInput");
  const currentQuantity = parseInt(quantityInput.value) || 1;

  if (currentQuantity > 1) {
    quantityInput.value = currentQuantity - 1;
    updateQuantityButtons();
  }
}

function updateQuantity() {
  const quantityInput = document.getElementById("quantityInput");
  const stockIndicator = document.getElementById("stockIndicator");
  const availableStock = parseInt(stockIndicator.textContent) || 0;

  let quantity = parseInt(quantityInput.value) || 1;

  // Ensure quantity is within bounds
  if (quantity < 1) {
    quantity = 1;
  } else if (quantity > availableStock && availableStock > 0) {
    quantity = availableStock;
  }

  quantityInput.value = quantity;
  updateQuantityButtons();
}

// Report product functionality
function reportProduct() {
  // Show a simple confirmation dialog
  const reasons = [
    "Inappropriate content",
    "Misleading information",
    "Copyright violation",
    "Counterfeit product",
    "Other",
  ];

  let message = "Why are you reporting this product?\n\n";
  reasons.forEach((reason, index) => {
    message += `${index + 1}. ${reason}\n`;
  });

  const choice = prompt(message + "\nEnter the number (1-5):");

  if (choice && choice >= 1 && choice <= 5) {
    const selectedReason = reasons[choice - 1];
    alert(
      `Thank you for your report. We will review this product for: ${selectedReason}`
    );

    // Here you would typically send the report to your backend
    console.log("Product reported for:", selectedReason);
  }
}

// Size guide scroll functionality
function scrollToSizeGuide(event) {
  event.preventDefault();

  // First, switch to the Product Details tab if not already active
  const productDetailsTab = document.querySelector(
    '.tab-btn[onclick*="product-details"]'
  );
  if (productDetailsTab && !productDetailsTab.classList.contains("active")) {
    switchTab(productDetailsTab, "product-details");
  }

  // Wait a moment for tab switch animation, then scroll
  setTimeout(() => {
    const sizeGuideSection = document.querySelector(".size-guide");
    if (sizeGuideSection) {
      sizeGuideSection.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

      // Add a subtle highlight effect
      sizeGuideSection.style.transition = "background-color 0.3s ease";
      sizeGuideSection.style.backgroundColor = "rgba(142, 68, 173, 0.05)";

      setTimeout(() => {
        sizeGuideSection.style.backgroundColor = "transparent";
      }, 2000);
    }
  }, 100);
}

// Zoom box functionality
function showZoomBox(event) {
  const zoomBox = document.getElementById("zoomBox");
  const zoomViewer = document.getElementById("zoomViewer");
  const zoomImage = document.getElementById("zoomImage");
  const mainImage = event.currentTarget;
  const mainImg = mainImage.querySelector("img");
  const rect = mainImage.getBoundingClientRect();

  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  // Position zoom box
  let boxX = x - 75;
  let boxY = y - 75;

  // Keep zoom box within image bounds
  boxX = Math.max(0, Math.min(boxX, rect.width - 150));
  boxY = Math.max(0, Math.min(boxY, rect.height - 150));

  zoomBox.style.display = "block";
  zoomBox.style.left = boxX + "px";
  zoomBox.style.top = boxY + "px";

  // Show zoom viewer
  zoomViewer.style.display = "block";

  // Calculate the percentage position of the zoom box center
  const percentX = (boxX + 75) / rect.width;
  const percentY = (boxY + 75) / rect.height;

  // Position the zoomed image (8x magnification for extreme fabric detail viewing)
  const zoomImageX = -(percentX * zoomImage.offsetWidth - 175);
  const zoomImageY = -(percentY * zoomImage.offsetHeight - 175);

  zoomImage.style.transform = `translate(${zoomImageX}px, ${zoomImageY}px)`;
}

function hideZoomBox() {
  const zoomBox = document.getElementById("zoomBox");
  const zoomViewer = document.getElementById("zoomViewer");
  zoomBox.style.display = "none";
  zoomViewer.style.display = "none";
}

// Populate the product detail page with a product object fetched from API
window.populateProductDetail = function (product) {
  try {
    if (!product) return;

    // set page product id for addToBag
    const container = document.querySelector(".container") || document.body;
    container.dataset.productId = product.id;

    // Title
    const titleEl = document.querySelector(".product-title");
    if (titleEl) titleEl.textContent = product.name || "";

    // Price
    const priceMain = document.querySelector(".price-main");
    if (priceMain)
      priceMain.textContent = `₱${Number(product.price || 0).toLocaleString()}`;

    // Original price
    const originalEl = document.querySelector(".original-price");
    if (originalEl) {
      if (product.originalPrice) {
        originalEl.textContent = `₱${Number(
          product.originalPrice
        ).toLocaleString()}`;
        originalEl.style.display = "";
      } else {
        originalEl.style.display = "none";
      }
    }

    // Materials / description
    const descEl = document.querySelector(
      ".product-info-sections .info-section p"
    );
    if (descEl && product.description) descEl.textContent = product.description;

    // Images
    const mainImage = document.getElementById("mainImage");
    const zoomImage = document.getElementById("zoomImage");
    const thumbnails = document.querySelectorAll(".thumbnail");
    const primary = product.primaryImage || product.primary_image || "";
    const secondary = product.secondaryImage || product.secondary_image || "";

    if (mainImage && primary) mainImage.src = primary;
    if (zoomImage && primary) zoomImage.src = primary;

    if (thumbnails && thumbnails.length > 0) {
      thumbnails.forEach((t, idx) => {
        if (idx === 0) t.src = primary;
        else if (idx === 1)
          t.src =
            secondary ||
            (product.variant_photos &&
              Object.values(product.variant_photos)[0] &&
              Object.values(product.variant_photos)[0].secondary) ||
            "";
      });
      thumbnails.forEach((thumb) => thumb.classList.remove("active"));
      if (thumbnails[0]) thumbnails[0].classList.add("active");
    }

    // Variant photo map (for selectColor to use)
    window.variantPhotoMap =
      product.variant_photos || window.variantPhotoMap || {};

    // Stock data and color buttons
    const stockData = product.stock_data || {};
    window._pageStockData = stockData;

    const colorContainer = document.querySelector(".color-options");
    if (colorContainer) {
      // Clear existing
      colorContainer.innerHTML = "";
      Object.keys(stockData).forEach((color, idx) => {
        const sizes = stockData[color] || {};
        const btn = document.createElement("button");
        btn.className = "color-option" + (idx === 0 ? " active" : "");
        btn.setAttribute("data-color", color);
        btn.setAttribute("data-stock", JSON.stringify(sizes));
        btn.setAttribute("title", color);
        // Attempt to set background color if it's a valid CSS color string
        try {
          btn.style.backgroundColor = color.toLowerCase();
        } catch (e) {
          btn.style.backgroundColor = "gray";
        }
        btn.addEventListener("click", function (ev) {
          ev.stopPropagation();
          selectColor(this);
        });
        colorContainer.appendChild(btn);
      });
    }

    // After re-building colors/sizes, update availability and stock UI
    setTimeout(() => {
      try {
        updateSizeAvailability();
        updateColorAvailability();
        updateStockDisplay();
      } catch (e) {
        console.warn("Error updating availability after populate", e);
      }
    }, 30);

    console.log("Product detail populated for", product.id);
  } catch (err) {
    console.error("populateProductDetail error", err);
  }
};
