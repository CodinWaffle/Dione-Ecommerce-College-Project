// Global variables
let currentImageIndex = 0;
const totalImages = 3;

// Make simple functions available immediately
if (typeof window !== 'undefined') {
  // Simple color selection that definitely works
  window.simpleSelectColor = function(button) {
    console.log("=== SIMPLE SELECT COLOR CALLED ===", button.dataset.color);
    
    // Remove active from all
    document.querySelectorAll('.color-option').forEach(btn => {
      btn.classList.remove('active');
      btn.style.transform = '';
      btn.style.boxShadow = '';
    });
    
    // Add active to clicked
    button.classList.add('active');
    button.style.transform = 'scale(1.1)';
    button.style.boxShadow = '0 0 0 3px rgba(142, 68, 173, 0.3)';
    
    // Update text
    const span = document.querySelector('.selected-color');
    if (span) span.textContent = button.dataset.color;
    
    // Update global state
    window.selectedColor = button.dataset.color;
    
    console.log('Color selected:', button.dataset.color);
    
    // Load sizes  
    window.loadSizesForColor(button.dataset.color, button);
  };
  
  // Function to load sizes
  window.loadSizesForColor = function(colorName, colorButton) {
    console.log('Loading sizes for color:', colorName);
    
    const sizeContainer = document.getElementById('sizeOptions');
    if (!sizeContainer) {
      console.error('Size container not found!');
      return;
    }
    
    try {
      // Get stock data from button
      const stockData = JSON.parse(colorButton.dataset.stock || '{}');
      console.log('Stock data for color:', stockData);
      
      // Clear container
      sizeContainer.innerHTML = '';
      
      // Create size buttons
      Object.keys(stockData).forEach(size => {
        const stock = stockData[size];
        const sizeBtn = document.createElement('button');
        sizeBtn.className = 'size-option' + (stock > 0 ? '' : ' out-of-stock');
        sizeBtn.textContent = size;
        sizeBtn.dataset.size = size;
        sizeBtn.dataset.stock = stock;
        sizeBtn.onclick = () => window.simpleSelectSize(sizeBtn);
        sizeContainer.appendChild(sizeBtn);
      });
      
      console.log('Sizes loaded successfully');
    } catch (e) {
      console.error('Error loading sizes:', e);
      sizeContainer.innerHTML = '<div class="error">Error loading sizes</div>';
    }
  };
  
  // Simple size selection
  window.simpleSelectSize = function(button) {
    console.log("=== SIMPLE SELECT SIZE CALLED ===", button.dataset.size);
    
    // Remove active from all size buttons
    document.querySelectorAll('.size-option').forEach(btn => {
      btn.classList.remove('active');
      btn.style.transform = '';
      btn.style.boxShadow = '';
    });
    
    // Add active to clicked
    button.classList.add('active');
    button.style.transform = 'scale(1.05)';
    button.style.boxShadow = '0 2px 8px rgba(142, 68, 173, 0.3)';
    
    // Update global state
    window.selectedSize = button.dataset.size;
    
    console.log('Size selected:', button.dataset.size);
  };
}

// Helper function to convert hex color to rgba
function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

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
  console.log("=== PRODUCT DETAIL DEBUG START ===");
  console.log("Product detail page loaded, initializing...");
  
  // Debug: Check if critical DOM elements exist
  const colorOptions = document.querySelectorAll(".color-option");
  const sizeContainer = document.getElementById("sizeOptions");
  
  console.log("Found elements:");
  console.log("- Color options:", colorOptions.length);
  console.log("- Size container:", sizeContainer ? "YES" : "NO");
  
  if (colorOptions.length === 0) {
    console.error("❌ No color options found! Check if product has variants.");
    return;
  }

  // Initialize stock display and availability
  try {
    console.log("Attaching event listeners...");
    // First attach event listeners
    attachVariantEventListeners();
    
    console.log("Updating displays...");
    // Then update displays
    updateColorAvailability();
    updateStockDisplay();
    updateModelInfo();
    hideColorSectionIfEmpty();
    
    // Initialize with placeholder sizes message
    initializeSizeDisplay();
    
    console.log("✅ Initialization completed successfully");
  } catch (e) {
    console.error("❌ Error initializing product detail:", e);
  }

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

  // Add event listeners to color and size options (in case onclick doesn't work)
  attachVariantEventListeners();

  console.log("Product detail initialization complete");
});

// Backup initialization on window load
window.addEventListener("load", function () {
  console.log("Window loaded, running backup initialization...");

  // Re-attach event listeners as backup
  setTimeout(() => {
    try {
      attachVariantEventListeners();
      console.log("Backup event listener attachment complete");
    } catch (e) {
      console.warn("Backup initialization failed:", e);
    }
  }, 100);
});

// Function to attach event listeners to color and size options
function attachVariantEventListeners() {
  // Attach color option event listeners
  const colorOptions = document.querySelectorAll(".color-option");
  
  console.log(`Found ${colorOptions.length} color options to attach listeners to`);
  
  // Apply color hex to swatches and ensure no default active state
  colorOptions.forEach((btn) => {
    try {
      const hex = btn.dataset.colorHex || btn.getAttribute("data-color-hex");
      if (hex) {
        btn.style.backgroundColor = hex;
        console.log(`Applied color ${hex} to button for ${btn.dataset.color}`);
      }
    } catch (e) {
      console.warn("Error applying color hex:", e);
    }
    // remove any accidental active class so sizes only show after user clicks
    btn.classList.remove("active");
  });
  
  colorOptions.forEach((colorBtn, index) => {
    // Remove any existing event listeners first
    if (colorBtn._clickHandler) {
      colorBtn.removeEventListener("click", colorBtn._clickHandler);
    }

    // Always attach click handler so colors are selectable even when stock is 0
    colorBtn._clickHandler = function (e) {
      e.preventDefault();
      e.stopPropagation();
      console.log(`Color button clicked:`, this.dataset.color);
      
      // Allow selection even if marked as disabled/out-of-stock
      if (this.classList.contains('disabled') || this.classList.contains('out-of-stock')) {\n        console.log('Selecting out-of-stock color:', this.dataset.color);\n      }\n      \n      selectColor(this);
    };
    colorBtn.addEventListener("click", colorBtn._clickHandler);
    
    // Ensure the button is not truly disabled (disabled attribute prevents events)
    colorBtn.removeAttribute('disabled');
    \n    console.log(`Attached click handler to color option ${index + 1}: ${colorBtn.dataset.color}`);\n  });

  // Attach size option event listeners
  const sizeOptions = document.querySelectorAll(".size-option");
  sizeOptions.forEach((sizeBtn) => {
    // Remove any existing event listeners first
    sizeBtn.removeEventListener("click", sizeBtn._clickHandler);

    // Always attach click handler so sizes are selectable even when stock is 0
    sizeBtn._clickHandler = function (e) {
      e.preventDefault();
      e.stopPropagation();
      selectSize(this);
    };
    sizeBtn.addEventListener("click", sizeBtn._clickHandler);
  });

  console.log(
    `Attached event listeners to ${colorOptions.length} color options and ${sizeOptions.length} size options`
  );
}

// Make functions globally accessible for onclick attributes
window.selectColor = selectColor;
window.selectSize = selectSize;
window.changeMainImage = changeMainImage;
window.addToBag = addToBag;
window.increaseQuantity = increaseQuantity;
window.decreaseQuantity = decreaseQuantity;
window.updateQuantity = updateQuantity;
window.reportProduct = reportProduct;
window.scrollToSizeGuide = scrollToSizeGuide;
window.navigateToHome = navigateToHome;
window.navigateToCategory = navigateToCategory;
window.switchTab = switchTab;
window.toggleSection = toggleSection;

// Test global function availability after DOM load
setTimeout(() => {
  console.log("Testing global functions:");
  console.log("window.selectColor:", typeof window.selectColor);
  console.log("window.selectSize:", typeof window.selectSize);
  
  // Add a test function to check color selection
  window.testColorSelection = function() {
    console.log("=== Testing Color Selection ===");
    const colorOptions = document.querySelectorAll(".color-option");
    console.log("Found", colorOptions.length, "color options");
    
    if (colorOptions.length > 0) {
      console.log("Attempting to select first color...");
      const firstColor = colorOptions[0];
      console.log("First color data:", {
        color: firstColor.dataset.color,
        colorHex: firstColor.dataset.colorHex,
        classList: firstColor.classList.toString()
      });
      
      try {
        selectColor(firstColor);
        console.log("selectColor function executed successfully");
      } catch (e) {
        console.error("Error calling selectColor:", e);
      }
    } else {
      console.log("No color options found");
    }
  };
  
  console.log("Test function added: window.testColorSelection()");
}, 500);

// Simple color selection function that definitely works
window.simpleSelectColor = function(button) {
  console.log("=== SIMPLE SELECT COLOR CALLED ===", button.dataset.color);
  
  // Remove active from all
  document.querySelectorAll('.color-option').forEach(btn => {
    btn.classList.remove('active');
    btn.style.transform = '';
    btn.style.boxShadow = '';
  });
  
  // Add active to clicked
  button.classList.add('active');
  button.style.transform = 'scale(1.1)';
  button.style.boxShadow = '0 0 0 3px rgba(142, 68, 173, 0.3)';
  
  // Update text
  const span = document.querySelector('.selected-color');
  if (span) span.textContent = button.dataset.color;
  
  // Update global state
  window.selectedColor = button.dataset.color;
  
  console.log('Color selected:', button.dataset.color);
  
  // Load sizes
  loadSizesForColor(button.dataset.color, button);
};

// Function to load sizes for selected color
function loadSizesForColor(colorName, colorButton) {
  console.log('Loading sizes for color:', colorName);
  
  const sizeContainer = document.getElementById('sizeOptions');
  if (!sizeContainer) {
    console.error('Size container not found!');
    return;
  }
  
  try {
    // Get stock data from button
    const stockData = JSON.parse(colorButton.dataset.stock || '{}');
    console.log('Stock data for color:', stockData);
    
    // Clear container
    sizeContainer.innerHTML = '';
    
    // Create size buttons
    Object.keys(stockData).forEach(size => {
      const stock = stockData[size];
      const sizeBtn = document.createElement('button');
      sizeBtn.className = 'size-option' + (stock > 0 ? '' : ' out-of-stock');
      sizeBtn.textContent = size;
      sizeBtn.dataset.size = size;
      sizeBtn.dataset.stock = stock;
      sizeBtn.onclick = () => window.simpleSelectSize(sizeBtn);
      sizeContainer.appendChild(sizeBtn);
    });
    
    console.log('Sizes loaded successfully');
  } catch (e) {
    console.error('Error loading sizes:', e);
    sizeContainer.innerHTML = '<div class="error">Error loading sizes</div>';
  }
}

// Simple size selection function
window.simpleSelectSize = function(button) {
  console.log("=== SIMPLE SELECT SIZE CALLED ===", button.dataset.size);
  
  // Remove active from all size buttons
  document.querySelectorAll('.size-option').forEach(btn => {
    btn.classList.remove('active');
    btn.style.transform = '';
    btn.style.boxShadow = '';
  });
  
  // Add active to clicked
  button.classList.add('active');
  button.style.transform = 'scale(1.05)';
  button.style.boxShadow = '0 2px 8px rgba(142, 68, 173, 0.3)';
  
  // Update global state
  window.selectedSize = button.dataset.size;
  
  console.log('Size selected:', button.dataset.size);
};

// Global variables for stock management
let currentSelectedColor = "Black";
let currentSelectedSize = "XS";

// Update stock display - shows exact stock for selected color+size combination
function updateStockDisplay() {
  const stockIndicator = document.getElementById("stockIndicator");
  const activeColorBtn = document.querySelector(".color-option.active");
  const activeSizeBtn = document.querySelector(".size-option.active");

  let stock = 0;
  let selectedColor =
    activeColorBtn?.dataset?.color ||
    window.selectedColor ||
    currentSelectedColor;
  let selectedSize =
    activeSizeBtn?.dataset?.size || window.selectedSize || currentSelectedSize;

  console.log(
    "updateStockDisplay called - selectedColor:",
    selectedColor,
    "selectedSize:",
    selectedSize
  );

  try {
    // Priority 1: Get stock from the specific color+size combination
    if (selectedColor && selectedSize) {
      // First try to get from global stock data
      const stockData = window._pageStockData || window.stockData || {};
      if (
        stockData[selectedColor] &&
        stockData[selectedColor][selectedSize] !== undefined
      ) {
        stock = parseInt(stockData[selectedColor][selectedSize]) || 0;
        console.log(
          "Stock from global stockData for",
          selectedColor,
          selectedSize,
          ":",
          stock
        );
      }
      // Fallback: try to get from active size button's data-stock attribute
      else if (activeSizeBtn && activeSizeBtn.dataset.stock !== undefined) {
        stock = parseInt(activeSizeBtn.dataset.stock) || 0;
        console.log("Stock from size button data-stock:", stock);
      }
      // Fallback: try to get from color button's stock data
      else if (activeColorBtn && activeColorBtn.dataset.stock) {
        try {
          const colorStock = JSON.parse(activeColorBtn.dataset.stock);
          stock = parseInt(colorStock[selectedSize]) || 0;
          console.log("Stock from color button stock data:", stock);
        } catch (e) {
          console.warn("Error parsing color stock data:", e);
        }
      }
    }
    // Priority 2: If only size is selected (no color variants)
    else if (selectedSize && activeSizeBtn) {
      stock = parseInt(activeSizeBtn.dataset.stock) || 0;
      console.log("Stock from size only:", stock);
    }
    // Priority 3: If only color is selected (show message to select size)
    else if (selectedColor && !selectedSize) {
      stock = 0;
      console.log(
        "Color selected but no size - showing 0 to encourage size selection"
      );
    }
    // Priority 4: No specific selection - show 0 or total if no variants
    else {
      const stockData = window._pageStockData || window.stockData || {};
      if (Object.keys(stockData).length === 0) {
        // No variants - show total product stock
        const productData = window._pageProductData || {};
        stock = productData.total_stock || 0;
        console.log("No variants - showing total stock:", stock);
      } else {
        // Has variants but none selected - show 0
        stock = 0;
        console.log("Has variants but none selected - showing 0");
      }
    }
  } catch (error) {
    console.error("Error calculating stock:", error);
    stock = 0;
  }

  console.log(
    "Final calculated stock for",
    selectedColor,
    selectedSize,
    ":",
    stock
  );

  // Update stock indicator display
  if (stockIndicator) {
    stockIndicator.textContent = stock.toString();

    // Update stock indicator styling
    stockIndicator.className = "stock-indicator";
    if (stock === 0) {
      stockIndicator.classList.add("out-of-stock");
    } else if (stock <= 3) {
      stockIndicator.classList.add("low-stock");
    } else {
      stockIndicator.classList.add("in-stock");
    }
  }

  // Update add to bag button state
  const addToBagBtn = document.querySelector(".add-to-bag-btn");
  if (addToBagBtn) {
    if (
      stock === 0 ||
      (!selectedColor && Object.keys(window._pageStockData || {}).length > 0) ||
      (!selectedSize && selectedColor)
    ) {
      addToBagBtn.disabled = true;
      if (
        !selectedColor &&
        Object.keys(window._pageStockData || {}).length > 0
      ) {
        addToBagBtn.textContent = "SELECT COLOR";
      } else if (!selectedSize && selectedColor) {
        addToBagBtn.textContent = "SELECT SIZE";
      } else {
        addToBagBtn.textContent = "OUT OF STOCK";
      }
      addToBagBtn.style.opacity = "0.6";
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
  }

  // Update quantity input max value
  const quantityInput = document.getElementById("quantityInput");
  if (quantityInput) {
    quantityInput.max = Math.max(1, stock);
    const currentQty = parseInt(quantityInput.value) || 1;
    if (currentQty > stock && stock > 0) {
      quantityInput.value = stock;
    } else if (stock === 0) {
      quantityInput.value = 1;
    }
  }

  // Update quantity buttons when stock changes
  updateQuantityButtons();
}

// Initialize size display with proper placeholder
function initializeSizeDisplay() {
  const sizeOptionsContainer = document.getElementById("sizeOptions");
  if (sizeOptionsContainer && !document.querySelector(".color-option.active")) {
    sizeOptionsContainer.innerHTML = '<div class="size-placeholder">Select a color to view available sizes</div>';
  }
}

// Update size availability based on color - Enhanced with database fetch
function updateSizeAvailability() {
  const activeColorBtn = document.querySelector(".color-option.active");
  const sizeOptionsContainer = document.getElementById("sizeOptions");

  console.log("updateSizeAvailability called, activeColorBtn:", activeColorBtn);

  if (!sizeOptionsContainer) {
    console.error("Size options container not found");
    return;
  }

  if (!activeColorBtn) {
    console.log("No active color selected, showing placeholder");
    sizeOptionsContainer.innerHTML = '<div class="size-placeholder">Select a color to view available sizes</div>';
    return;
  }

  const selectedColor = activeColorBtn.dataset.color;
  const productId =
    window.productId ||
    document.querySelector("[data-product-id]")?.dataset.productId;

  if (!productId) {
    console.error("Product ID not found");
    return;
  }

  console.log("Fetching sizes for color:", selectedColor, "product:", productId);

  // Show loading state
  sizeOptionsContainer.innerHTML =
    '<div class="loading-sizes">Loading sizes...</div>';

  // Fetch sizes for the selected color from database
  fetch(
    `/api/product/${productId}/sizes/${encodeURIComponent(selectedColor)}`
  )
    .then((response) => {
      console.log("Fetch response status:", response.status);
      return response.json();
    })
    .then((data) => {
      console.log("Fetch response data:", data);
      if (data.success && data.sizes) {
        // Clear loading state
        sizeOptionsContainer.innerHTML = "";

        // Create size options for the selected color
        let firstAvailableSize = null;
        const sizesData = data.sizes;

        // Sort sizes in a logical order (XS, S, M, L, XL, etc.)
        const sizeOrder = [
          "XS",
          "S",
          "M",
          "L",
          "XL",
          "XXL",
          "3XL",
          "4XL",
          "5XL",
        ];
        const sortedSizes = Object.keys(sizesData).sort((a, b) => {
          const aIndex = sizeOrder.indexOf(a);
          const bIndex = sizeOrder.indexOf(b);
          if (aIndex !== -1 && bIndex !== -1) {
            return aIndex - bIndex;
          }
          if (aIndex !== -1) return -1;
          if (bIndex !== -1) return 1;
          return a.localeCompare(b);
        });

        console.log("Creating size buttons for sizes:", sortedSizes);

        sortedSizes.forEach((size) => {
          const sizeInfo = sizesData[size];
          const stock = sizeInfo.stock || 0;
          const isAvailable = sizeInfo.available && stock > 0;

          if (isAvailable && !firstAvailableSize) {
            firstAvailableSize = size;
          }

          const sizeBtn = document.createElement("button");
          sizeBtn.className = `size-option ${
            !isAvailable ? "out-of-stock" : ""
          }`;
          sizeBtn.setAttribute("data-size", size);
          sizeBtn.setAttribute("data-stock", stock);
          sizeBtn.textContent = size;

          // Add stock info as tooltip
          sizeBtn.title = `${size} - ${stock} in stock`;

          // Always attach selection handler so users can pick sizes even when stock is 0
          sizeBtn.onclick = () => selectSize(sizeBtn);
          sizeBtn._clickHandler = function (e) {
            e.preventDefault();
            e.stopPropagation();
            selectSize(this);
          };
          sizeBtn.addEventListener("click", sizeBtn._clickHandler);

          sizeOptionsContainer.appendChild(sizeBtn);
        });

          // Clear current selected size when color changes to force user selection
          currentSelectedSize = null;
          window.selectedSize = null;

          // Update stock display to show 0 until size is selected
          updateStockDisplay();

          console.log(
            `Loaded ${sortedSizes.length} sizes for color ${selectedColor}`
          );
        } else {
          // Handle error or no sizes found
          sizeOptionsContainer.innerHTML =
            '<div class="no-sizes">No sizes available for this color</div>';
          console.error("Failed to load sizes:", data.error || "Unknown error");
        }
      })
      .catch((error) => {
        console.error("Error fetching sizes:", error);
        // Fallback to original method using dataset.stock
        try {
          const colorStock = JSON.parse(activeColorBtn.dataset.stock || "{}");
          sizeOptionsContainer.innerHTML = "";

          Object.keys(colorStock).forEach((size) => {
            const stock = colorStock[size];
            const isAvailable = stock > 0;

            const sizeBtn = document.createElement("button");
            sizeBtn.className = `size-option ${
              !isAvailable ? "out-of-stock" : ""
            }`;
            sizeBtn.setAttribute("data-size", size);
            sizeBtn.setAttribute("data-stock", stock);
            sizeBtn.textContent = size;
            sizeBtn.onclick = () => selectSize(sizeBtn);
            sizeOptionsContainer.appendChild(sizeBtn);
          });

          console.log("Used fallback method for sizes");
        } catch (fallbackError) {
          sizeOptionsContainer.innerHTML =
            '<div class="error-sizes">Error loading sizes</div>';
          console.error("Fallback method also failed:", fallbackError);
        }
      });
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

      // Mark out-of-stock visually but keep interactive so users can still select
      if (stock === 0) {
        colorBtn.classList.add("out-of-stock");
      } else {
        colorBtn.classList.remove("out-of-stock");
      }
      // Ensure click handler exists (it should from attachVariantEventListeners)
      if (!colorBtn._clickHandler) {
        colorBtn._clickHandler = function (e) {
          e.preventDefault();
          e.stopPropagation();
          selectColor(this);
        };
        colorBtn.addEventListener("click", colorBtn._clickHandler);
      }
    });
  }
}

// Color selection
function selectColor(colorBtn) {
  console.log("selectColor called with:", colorBtn);
  
  // Use the simple version that we know works
  try {
    window.simpleSelectColor(colorBtn);
    return;
  } catch (e) {
    console.error("Simple select color failed, trying complex version:", e);
  }

  // Allow selection even if visually marked out-of-stock; addToBag will still
  // prevent adding items with 0 stock.

  // Ensure we have a valid button element
  if (!colorBtn || !colorBtn.dataset) {
    console.error("Invalid color button element");
    return;
  }

  const colorOptions = document.querySelectorAll(".color-option");
  const selectedColorSpan = document.querySelector(".selected-color");

  // Remove active class from all color options
  colorOptions.forEach((option) => {
    option.classList.remove("active");
    option.style.transform = "";
    option.style.boxShadow = "";
  });
  
  // Add active class and visual feedback to selected color
  colorBtn.classList.add("active");
  colorBtn.style.transform = "scale(1.1)";
  colorBtn.style.boxShadow = "0 0 0 3px rgba(142, 68, 173, 0.3)";
  
  console.log("Active class added to color button:", colorBtn.classList.contains("active"));

  // Update UI text
  if (selectedColorSpan) {
    selectedColorSpan.textContent = colorBtn.dataset.color;
    console.log("Updated selected color span to:", selectedColorSpan.textContent);
  } else {
    console.warn("Selected color span not found");
  }
  
  // Update global state
  currentSelectedColor = colorBtn.dataset.color;
  window.selectedColor = colorBtn.dataset.color;
  
  console.log("Color selected:", currentSelectedColor);

  // Set CSS custom properties for dynamic color scheme
  const colorHex = colorBtn.dataset.colorHex || "#8e44ad";
  const root = document.documentElement;
  root.style.setProperty("--selected-color", colorHex);

  // Create lighter version for hover effects
  const lightColor = hexToRgba(colorHex, 0.1);
  const shadowColor = hexToRgba(colorHex, 0.4);
  root.style.setProperty("--selected-color-light", lightColor);
  root.style.setProperty("--selected-color-shadow", shadowColor);

  // Update size availability and stock display
  console.log("Updating size availability for color:", currentSelectedColor);
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
        // Update main image immediately
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

          // Set first thumbnail as active and update current image index
          thumbnails.forEach((thumb) => thumb.classList.remove("active"));
          if (thumbnails[0]) {
            thumbnails[0].classList.add("active");
            currentImageIndex = 0;
          }
        }

        console.log(
          `Switched to ${colorKey} variant images - Primary: ${primary}, Secondary: ${secondary}`
        );
      }
    } else {
      // Fallback to default product images if no variant images
      const productData = window._pageProductData || {};
      const defaultPrimary =
        productData.primaryImage || productData.primary_image;
      const defaultSecondary =
        productData.secondaryImage || productData.secondary_image;

      if (defaultPrimary && mainImage) {
        mainImage.src = defaultPrimary;
        if (zoomImage) zoomImage.src = defaultPrimary;

        if (thumbnails && thumbnails.length > 0) {
          thumbnails.forEach((t, idx) => {
            if (idx === 0) {
              t.src = defaultPrimary;
            } else if (idx === 1 && defaultSecondary) {
              t.src = defaultSecondary;
            } else {
              t.src = defaultPrimary;
            }
          });
        }
      }
    }
  } catch (err) {
    console.warn("Variant image swap failed", err);
  }

  // Update model information if available
  updateModelInfo();
}

// Enhanced size selection function
function selectSize(sizeBtn) {
  console.log("selectSize called with:", sizeBtn);

  // Ensure we have a valid button element
  if (!sizeBtn || !sizeBtn.dataset) {
    console.error("Invalid size button element");
    return;
  }

  const size = sizeBtn.dataset.size;
  const selectedColor =
    window.selectedColor ||
    currentSelectedColor ||
    document.querySelector(".color-option.active")?.dataset?.color;

  console.log("Selecting size:", size, "for color:", selectedColor);

  // Update selected size globally
  window.selectedSize = size;
  currentSelectedSize = size;

  // Update UI - remove selected class from all size buttons
  const sizeOptions = document.querySelectorAll(".size-option");
  sizeOptions.forEach((option) => {
    option.classList.remove("active");
    option.style.transform = "";
    option.style.boxShadow = "";
  });

  // Add selected class to clicked button
  sizeBtn.classList.add("active");

  // Get the actual stock for this color+size combination
  let actualStock = 0;
  if (selectedColor && size) {
    const stockData = window._pageStockData || window.stockData || {};
    actualStock = parseInt(stockData[selectedColor]?.[size]) || 0;
  } else {
    // Fallback to button's data-stock if no color variants
    actualStock = parseInt(sizeBtn.dataset.stock) || 0;
  }

  console.log("Actual stock for", selectedColor, size, ":", actualStock);

  // Add visual feedback for selected size
  if (actualStock > 0) {
    sizeBtn.style.transform = "scale(1.05)";
    sizeBtn.style.boxShadow = "0 2px 8px rgba(142, 68, 173, 0.3)";
  }

  // Update color availability and stock display
  updateColorAvailability();

  // Force immediate stock display update with better timing
  updateStockDisplay();

  // Update model information if available
  updateModelInfo();

  // Provide user feedback about stock level with animation
  const stockIndicator = document.getElementById("stockIndicator");
  if (stockIndicator) {
    // Add temporary highlight to stock indicator
    stockIndicator.style.transition = "all 0.3s ease";
    stockIndicator.style.transform = "scale(1.1)";

    if (actualStock === 0) {
      stockIndicator.style.color = "#dc2626";
      stockIndicator.style.fontWeight = "bold";
    } else if (actualStock <= 3) {
      stockIndicator.style.color = "#f59e0b";
      stockIndicator.style.fontWeight = "bold";
    } else {
      stockIndicator.style.color = "#059669";
      stockIndicator.style.fontWeight = "bold";
    }

    // Reset styling after animation
    setTimeout(() => {
      stockIndicator.style.fontWeight = "";
      stockIndicator.style.color = "";
      stockIndicator.style.transform = "";
    }, 1500);
  }

  // Update selected size display if it exists
  const selectedSizeSpan = document.querySelector(".selected-size");
  if (selectedSizeSpan) {
    selectedSizeSpan.textContent = size;
  }
}

// Wishlist toggle
document.getElementById("wishlistBtn").addEventListener("click", function () {
  this.classList.toggle("active");
});

// Add to bag functionality
function addToBag() {
  const addToBagBtn = document.querySelector(".add-to-bag-btn");

  // Add animation class
  if (addToBagBtn) {
    addToBagBtn.classList.add("adding");

    // Remove animation class after animation completes
    setTimeout(() => {
      addToBagBtn.classList.remove("adding");
    }, 600);
  }

  const selectedColorBtn = document.querySelector(".color-option.active");
  const selectedSizeBtn = document.querySelector(".size-option.active");

  if (!selectedColorBtn || !selectedSizeBtn) {
    // Show error message if color or size not selected
    if (addToBagBtn) {
      const originalText = addToBagBtn.innerHTML;
      addToBagBtn.innerHTML = "SELECT COLOR & SIZE";
      addToBagBtn.style.backgroundColor = "#e74c3c";

      setTimeout(() => {
        addToBagBtn.innerHTML = originalText;
        addToBagBtn.style.backgroundColor = "";
      }, 2000);
    }
    return;
  }

  const selectedColor = selectedColorBtn.dataset.color;
  const selectedSize = selectedSizeBtn.textContent;
  const selectedQuantity = document.getElementById("quantityInput").value;

  // Get product details from the page
  const productName = document.querySelector(".product-title").textContent;
  const productPrice = parseFloat(
    document.querySelector(".price-main").textContent.replace(/[₱,]/g, "")
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
  if (typeof showCartSuccessAnimation === "function") {
    showCartSuccessAnimation();
  }

  // Show success feedback
  if (addToBagBtn) {
    const originalText = addToBagBtn.innerHTML;
    addToBagBtn.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="20,6 9,17 4,12"></polyline>
      </svg>
      ADDED TO BAG
    `;
    addToBagBtn.style.backgroundColor = "#27ae60";

    setTimeout(() => {
      addToBagBtn.innerHTML = originalText;
      addToBagBtn.style.backgroundColor = "";
    }, 2000);
  }
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

// Update model information based on selected variant
function updateModelInfo() {
  const modelInfoEl = document.getElementById("modelInfo");
  if (!modelInfoEl) return;

  // Try to get model info from product data or use default
  const productData = window._pageProductData || {};
  const modelInfo = productData.details_fit || productData.model_info;

  if (modelInfo) {
    modelInfoEl.innerHTML = `<span>${modelInfo}</span>`;
  } else {
    // Keep default model info
    modelInfoEl.innerHTML = `<span>Model is 5'10", wearing a size S</span>`;
  }
}

// Hide color section if no variants available
function hideColorSectionIfEmpty() {
  const colorSection = document.querySelector(".color-section");
  const colorOptions = document.querySelectorAll(".color-option");

  console.log(
    "hideColorSectionIfEmpty - colorOptions found:",
    colorOptions.length
  );

  if (colorSection && colorOptions.length === 0) {
    colorSection.style.display = "none";
    console.log("Color section hidden - no variants");
  } else if (colorSection) {
    colorSection.style.display = "block";
    console.log("Color section shown - variants available");
  }
}

// Removed duplicate selectColor function - using the one that calls updateSizeAvailability() instead

// Removed updateSizeOptions function - using updateSizeAvailability() which calls the API instead

// Update product images when color is selected
function updateProductImages(selectedColor) {
  try {
    const variantMap = window.variantPhotoMap || {};
    const variant = variantMap[selectedColor];
    const mainImage = document.getElementById("mainImage");
    const zoomImage = document.getElementById("zoomImage");
    const thumbnails = document.querySelectorAll(".thumbnail");

    if (variant && mainImage) {
      // variant may be an object { primary: url, secondary: url, color_hex: hex } or a string
      const primary =
        typeof variant === "string"
          ? variant
          : variant.primary || variant.image || null;
      const secondary =
        typeof variant === "object" && variant.secondary
          ? variant.secondary
          : null;

      if (primary) {
        // Update main image with smooth transition
        mainImage.style.opacity = "0.7";
        setTimeout(() => {
          mainImage.src = primary;
          if (zoomImage) zoomImage.src = primary;
          mainImage.style.opacity = "1";
        }, 150);

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

          // Set first thumbnail as active and update current image index
          thumbnails.forEach((thumb) => thumb.classList.remove("active"));
          if (thumbnails[0]) {
            thumbnails[0].classList.add("active");
            currentImageIndex = 0;
          }
        }

        console.log(
          `Updated images for ${selectedColor} - Primary: ${primary}, Secondary: ${secondary}`
        );
      }
    } else {
      // Fallback to default product images if no variant images
      const productData = window._pageProductData || {};
      const defaultPrimary =
        productData.primaryImage || productData.primary_image;
      const defaultSecondary =
        productData.secondaryImage || productData.secondary_image;

      if (defaultPrimary && mainImage) {
        mainImage.style.opacity = "0.7";
        setTimeout(() => {
          mainImage.src = defaultPrimary;
          if (zoomImage) zoomImage.src = defaultPrimary;
          mainImage.style.opacity = "1";
        }, 150);

        if (thumbnails && thumbnails.length > 0) {
          thumbnails.forEach((t, idx) => {
            if (idx === 0) {
              t.src = defaultPrimary;
            } else if (idx === 1 && defaultSecondary) {
              t.src = defaultSecondary;
            } else {
              t.src = defaultPrimary;
            }
          });
        }
      }
    }
  } catch (err) {
    console.warn("Product image update failed", err);
  }
}

// Make functions globally accessible
window.selectColor = selectColor;
window.selectSize = selectSize;
window.updateProductImages = updateProductImages;

// Populate the product detail page with a product object fetched from API
window.populateProductDetail = function (product) {
  try {
    if (!product) return;

    // Store product data globally for reference
    window._pageProductData = product;

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
        const totalStock = Object.values(sizes).reduce(
          (sum, stock) => sum + (stock || 0),
          0
        );

        const btn = document.createElement("button");
        // keep interactive even when out-of-stock; use visual marker only
        btn.className =
          "color-option" +
          (idx === 0 ? " active" : "") +
          (totalStock === 0 ? " out-of-stock" : "");
        btn.setAttribute("data-color", color);
        btn.setAttribute("data-stock", JSON.stringify(sizes));
        btn.setAttribute("data-total-stock", totalStock);
        btn.setAttribute(
          "title",
          color + (totalStock === 0 ? " - Out of Stock" : "")
        );

        // Get color hex from variant photos or use color name
        const variantPhoto = window.variantPhotoMap[color];
        const colorHex =
          (variantPhoto && variantPhoto.color_hex) || color.toLowerCase();

        // Attempt to set background color
        try {
          btn.style.backgroundColor = colorHex;
        } catch (e) {
          btn.style.backgroundColor = "gray";
        }

        // Add out of stock styling
        if (totalStock === 0) {
          // visual OOS marker but keep interactive
          btn.style.opacity = "0.6";

          // Add OOS label
          const oosLabel = document.createElement("span");
          oosLabel.className = "oos-label";
          oosLabel.textContent = "OOS";
          oosLabel.style.cssText =
            "position: absolute; top: -8px; right: -8px; background: #dc143c; color: white; font-size: 8px; padding: 1px 3px; border-radius: 2px; font-weight: bold; z-index: 1;";
          btn.style.position = "relative";
          btn.appendChild(oosLabel);
        }

        // Always attach click handler so color can be selected
        btn.onclick = function () {
          selectColor(this);
        };
        btn.addEventListener("click", function (ev) {
          ev.preventDefault();
          ev.stopPropagation();
          selectColor(this);
        });

        colorContainer.appendChild(btn);
      });
    }

    // Hide color section if no variants
    hideColorSectionIfEmpty();

    // After re-building colors/sizes, update availability and stock UI
    setTimeout(() => {
      try {
        updateSizeAvailability();
        updateColorAvailability();
        updateStockDisplay();
        updateModelInfo();
      } catch (e) {
        console.warn("Error updating availability after populate", e);
      }
    }, 30);

    console.log("Product detail populated for", product.id);
  } catch (err) {
    console.error("populateProductDetail error", err);
  }
};
