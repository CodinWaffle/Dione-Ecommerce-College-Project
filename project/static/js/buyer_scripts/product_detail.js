// Global variables
let currentImageIndex = 0;
const totalImages = 3;

// Make simple functions available immediately
if (typeof window !== "undefined") {
  // Simple color selection that definitely works
  window.simpleSelectColor = function (button) {
    console.log("=== SIMPLE SELECT COLOR CALLED ===", button.dataset.color);

    // Remove active from all
    document.querySelectorAll(".color-option").forEach((btn) => {
      btn.classList.remove("active");
      btn.style.transform = "";
      btn.style.boxShadow = "";
    });

    // Add active to clicked
    button.classList.add("active");
    // Show error message if color or size not selected
    const originalText = addToBagBtn.innerHTML;
    addToBagBtn.innerHTML = "SELECT COLOR & SIZE";
    addToBagBtn.style.backgroundColor = "#e74c3c";
    setTimeout(() => {
      addToBagBtn.innerHTML = originalText;
      addToBagBtn.style.backgroundColor = "";
    }, 2000);
    return;
    button.style.boxShadow = "0 0 0 3px rgba(142, 68, 173, 0.3)";

    // Update text
    const span = document.querySelector(".selected-color");
    if (span) span.textContent = button.dataset.color;

    // Update global state
    window.selectedColor = button.dataset.color;

    console.log("Color selected:", button.dataset.color);

    // Load sizes
    window.loadSizesForColor(button.dataset.color, button);
  };

  // Function to load sizes
  window.loadSizesForColor = function (colorName, colorButton) {
    console.log("Loading sizes for color:", colorName);

    const sizeContainer = document.getElementById("sizeOptions");
    if (!sizeContainer) {
      console.error("Size container not found!");
      return;
    }

    try {
      // Get stock data from button
      const stockData = JSON.parse(colorButton.dataset.stock || "{}");
      console.log("Stock data for color:", stockData);

      // Clear container
      sizeContainer.innerHTML = "";

      // Create size buttons
      Object.keys(stockData).forEach((size) => {
        const stock = stockData[size];
        const sizeBtn = document.createElement("button");
        sizeBtn.className = "size-option" + (stock > 0 ? "" : " out-of-stock");
        sizeBtn.textContent = size;
        sizeBtn.dataset.size = size;
        sizeBtn.dataset.stock = stock;
        sizeBtn.onclick = () => window.simpleSelectSize(sizeBtn);
        sizeContainer.appendChild(sizeBtn);
      });

      console.log("Sizes loaded successfully");
    } catch (e) {
      console.error("Error loading sizes:", e);
      sizeContainer.innerHTML = '<div class="error">Error loading sizes</div>';
    }
  };

  // Simple size selection
  window.simpleSelectSize = function (button) {
    console.log("=== SIMPLE SELECT SIZE CALLED ===", button.dataset.size);

    // Remove active from all size buttons
    document.querySelectorAll(".size-option").forEach((btn) => {
      btn.classList.remove("active");
      btn.style.transform = "";
      btn.style.boxShadow = "";
    });

    // Add active to clicked
    button.classList.add("active");
    button.style.transform = "scale(1.05)";
    button.style.boxShadow = "0 2px 8px rgba(142, 68, 173, 0.3)";

    // Update global state
    window.selectedSize = button.dataset.size;

    console.log("Size selected:", button.dataset.size);
  };

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
      console.warn(
        "⚠️ No color option elements found in DOM — attempting to fetch product data from API"
      );

      // Try to fetch product JSON from API (useful if the server didn't render variant buttons)
      const productId =
        document.querySelector("[data-product-id]")?.dataset.productId ||
        document.querySelector(".container")?.dataset.productId;

      if (productId) {
        (async () => {
          try {
            const resp = await fetch(`/api/product/${productId}`);
            if (!resp.ok) {
              console.warn("Product fetch returned non-ok status", resp.status);
            } else {
              const pj = await resp.json();
              const productObj = pj.product || pj;
              if (productObj) {
                console.log(
                  "Fetched product JSON, populating page",
                  productObj.id
                );
                populateProductDetail(productObj);
              }
            }
          } catch (e) {
            console.warn(
              "Failed to fetch product JSON for populateProductDetail:",
              e
            );
          }
        })();
      } else {
        console.warn("No productId found in DOM to fetch product JSON");
      }

      // continue initialization even if color options are not present yet
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

    console.log(
      `Found ${colorOptions.length} color options to attach listeners to`
    );

    // Apply color hex to swatches and ensure no default active state
    colorOptions.forEach((btn) => {
      try {
        const hex = btn.dataset.colorHex || btn.getAttribute("data-color-hex");
        if (hex) {
          btn.style.backgroundColor = hex;
          console.log(
            `Applied color ${hex} to button for ${btn.dataset.color}`
          );
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
        if (
          this.classList.contains("disabled") ||
          this.classList.contains("out-of-stock")
        ) {
          console.log("Selecting out-of-stock color:", this.dataset.color);
        }

        selectColor(this);
      };
      colorBtn.addEventListener("click", colorBtn._clickHandler);

      // Ensure the button is not truly disabled (disabled attribute prevents events)
      colorBtn.removeAttribute("disabled");
      console.log(
        `Attached click handler to color option ${index + 1}: ${
          colorBtn.dataset.color
        }`
      );
    });

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
    window.testColorSelection = function () {
      console.log("=== Testing Color Selection ===");
      const colorOptions = document.querySelectorAll(".color-option");
      console.log("Found", colorOptions.length, "color options");

      if (colorOptions.length > 0) {
        console.log("Attempting to select first color...");
        const firstColor = colorOptions[0];
        console.log("First color data:", {
          color: firstColor.dataset.color,
          colorHex: firstColor.dataset.colorHex,
          classList: firstColor.classList.toString(),
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
  window.simpleSelectColor = function (button) {
    console.log("=== SIMPLE SELECT COLOR CALLED ===", button.dataset.color);

    // Remove active from all
    document.querySelectorAll(".color-option").forEach((btn) => {
      btn.classList.remove("active");
      btn.style.transform = "";
      btn.style.boxShadow = "";
    });

    // Add active to clicked
    button.classList.add("active");
    button.style.transform = "scale(1.1)";
    button.style.boxShadow = "0 0 0 3px rgba(142, 68, 173, 0.3)";

    // Update text
    const span = document.querySelector(".selected-color");
    if (span) span.textContent = button.dataset.color;

    // Update global state
    window.selectedColor = button.dataset.color;

    console.log("Color selected:", button.dataset.color);

    // Load sizes
    loadSizesForColor(button.dataset.color, button);
  };

  // Function to load sizes for selected color
  function loadSizesForColor(colorName, colorButton) {
    console.log("Loading sizes for color:", colorName);

    const sizeContainer = document.getElementById("sizeOptions");
    if (!sizeContainer) {
      console.error("Size container not found!");
      return;
    }

    try {
      // Get stock data from button
      const stockData = JSON.parse(colorButton.dataset.stock || "{}");
      console.log("Stock data for color:", stockData);

      // Clear container
      sizeContainer.innerHTML = "";

      // Create size buttons
      Object.keys(stockData).forEach((size) => {
        const stock = stockData[size];
        const sizeBtn = document.createElement("button");
        sizeBtn.className = "size-option" + (stock > 0 ? "" : " out-of-stock");
        sizeBtn.textContent = size;
        sizeBtn.dataset.size = size;
        sizeBtn.dataset.stock = stock;
        sizeBtn.onclick = () => window.simpleSelectSize(sizeBtn);
        sizeContainer.appendChild(sizeBtn);
      });

      console.log("Sizes loaded successfully");
    } catch (e) {
      console.error("Error loading sizes:", e);
      sizeContainer.innerHTML = '<div class="error">Error loading sizes</div>';
    }
  }

  // Simple size selection function
  window.simpleSelectSize = function (button) {
    console.log("=== SIMPLE SELECT SIZE CALLED ===", button.dataset.size);

    // Remove active from all size buttons
    document.querySelectorAll(".size-option").forEach((btn) => {
      btn.classList.remove("active");
      btn.style.transform = "";
      btn.style.boxShadow = "";
    });

    // Add active to clicked
    button.classList.add("active");
    button.style.transform = "scale(1.05)";
    button.style.boxShadow = "0 2px 8px rgba(142, 68, 173, 0.3)";

    // Update global state
    window.selectedSize = button.dataset.size;

    console.log("Size selected:", button.dataset.size);
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
      activeSizeBtn?.dataset?.size ||
      window.selectedSize ||
      currentSelectedSize;

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
        (!selectedColor &&
          Object.keys(window._pageStockData || {}).length > 0) ||
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
    if (
      sizeOptionsContainer &&
      !document.querySelector(".color-option.active")
    ) {
      sizeOptionsContainer.innerHTML =
        '<div class="size-placeholder">Select a color to view available sizes</div>';
    }
  }

  // Update size availability based on color - Enhanced with database fetch
  function updateSizeAvailability() {
    const activeColorBtn = document.querySelector(".color-option.active");
    const sizeOptionsContainer = document.getElementById("sizeOptions");

    console.log(
      "updateSizeAvailability called, activeColorBtn:",
      activeColorBtn
    );

    if (!sizeOptionsContainer) {
      console.error("Size options container not found");
      return;
    }

    if (!activeColorBtn) {
      console.log("No active color selected, showing placeholder");
      sizeOptionsContainer.innerHTML =
        '<div class="size-placeholder">Select a color to view available sizes</div>';
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

    console.log(
      "Fetching sizes for color:",
      selectedColor,
      "product:",
      productId
    );

    // Show loading state
    sizeOptionsContainer.innerHTML =
      '<div class="loading-sizes">Loading sizes...</div>';
    // If we already loaded product variants map earlier, prefer it (contains sku, size_id, stock)
    if (
      window._productVariants &&
      window._productVariants[selectedColor] &&
      Array.isArray(window._productVariants[selectedColor].sizes) &&
      window._productVariants[selectedColor].sizes.length > 0
    ) {
      const sizesArr = window._productVariants[selectedColor].sizes;
      sizeOptionsContainer.innerHTML = "";

      const sizeOrder = ["XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"];
      sizesArr.sort((a, b) => {
        const aIdx = sizeOrder.indexOf(a.size_label);
        const bIdx = sizeOrder.indexOf(b.size_label);
        if (aIdx !== -1 && bIdx !== -1) return aIdx - bIdx;
        if (aIdx !== -1) return -1;
        if (bIdx !== -1) return 1;
        return (a.size_label || "").localeCompare(b.size_label || "");
      });

      sizesArr.forEach((s) => {
        const stock = parseInt(s.stock || 0) || 0;
        const isAvailable = stock > 0 && !!s.available;

        const sizeBtn = document.createElement("button");
        sizeBtn.className = `size-option ${!isAvailable ? "out-of-stock" : ""}`;
        sizeBtn.setAttribute("data-size", s.size_label);
        if (s.size_id) sizeBtn.setAttribute("data-size-id", s.size_id);
        if (s.sku) sizeBtn.setAttribute("data-sku", s.sku);
        sizeBtn.setAttribute("data-stock", stock);
        sizeBtn.textContent = s.size_label;
        sizeBtn.title = `${s.size_label} - ${stock} in stock`;
        sizeBtn.onclick = () => selectSize(sizeBtn);
        sizeBtn._clickHandler = function (e) {
          e.preventDefault();
          e.stopPropagation();
          selectSize(this);
        };
        sizeBtn.addEventListener("click", sizeBtn._clickHandler);

        sizeOptionsContainer.appendChild(sizeBtn);
      });

      // Reset selection state
      currentSelectedSize = null;
      window.selectedSize = null;
      updateStockDisplay();
      console.log("Loaded sizes from _productVariants for", selectedColor);
      return;
    }

    // Fetch sizes for the selected color from database (fallback)
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

  console.log(
    "Active class added to color button:",
    colorBtn.classList.contains("active")
  );

  // Update UI text
  if (selectedColorSpan) {
    selectedColorSpan.textContent = colorBtn.dataset.color;
    console.log(
      "Updated selected color span to:",
      selectedColorSpan.textContent
    );
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

  // Resolve variant/size metadata if available
  const selectedSizeBtn = document.querySelector(".size-option.active");
  let variantId = null;
  let sizeId = null;
  let sku = null;
  let variantImage = null;
  let availableStock = null;

  if (selectedSizeBtn) {
    if (selectedSizeBtn.dataset.sizeId) sizeId = selectedSizeBtn.dataset.sizeId;
    if (selectedSizeBtn.dataset.sku) sku = selectedSizeBtn.dataset.sku;
    if (selectedSizeBtn.dataset.stock)
      availableStock = parseInt(selectedSizeBtn.dataset.stock) || 0;
  }

  // Try variants map
  try {
    if (window._productVariants && window._productVariants[selectedColor]) {
      const v = window._productVariants[selectedColor];
      if (v && v.variant_id) variantId = v.variant_id;
      if (!sizeId && Array.isArray(v.sizes)) {
        const found = v.sizes.find(
          (s) =>
            String(s.size_label) === String(selectedSize) ||
            s.size_label === selectedSizeBtn?.dataset.size
        );
        if (found) {
          sizeId = found.size_id || sizeId;
          sku = sku || found.sku || sku;
          availableStock =
            availableStock === null
              ? parseInt(found.stock || 0)
              : availableStock;
        }
      }
      // images
      if (v.images && v.images.length > 0) variantImage = v.images[0];
    }
  } catch (e) {
    console.warn("Error resolving variant from _productVariants", e);
  }

  // Fallback: if still no availableStock, try global page stock data
  if (availableStock === null) {
    try {
      const stockData = window._pageStockData || window.stockData || {};
      availableStock =
        parseInt(
          (stockData[selectedColor] &&
            stockData[selectedColor][selectedSize]) ||
            0
        ) || 0;
    } catch (e) {
      availableStock = 0;
    }
  }

  const qty = parseInt(selectedQuantity) || 1;
  if (qty > availableStock) {
    // show error
    if (addToBagBtn) {
      const originalText = addToBagBtn.innerHTML;
      addToBagBtn.innerHTML = `ONLY ${availableStock} LEFT`;
      addToBagBtn.style.backgroundColor = "#e74c3c";
      setTimeout(() => {
        addToBagBtn.innerHTML = originalText;
        addToBagBtn.style.backgroundColor = "";
      }, 2000);
    }
    return;
  }

  // Build payload for backend
  const payload = {
    product_id: productId,
    color: selectedColor,
    size: selectedSize,
    quantity: qty,
  };
  if (variantId) payload.variant_id = variantId;
  if (sizeId) payload.size_id = sizeId;
  if (sku) payload.sku = sku;

  // POST to add-to-cart endpoint with validation on server
  fetch("/add-to-cart", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((r) => r.json())
    .then((data) => {
      console.debug("/add-to-cart response:", data);
      if (data && data.success) {
        // Update popup using returned item data if present
        const item = data.item || {};
        console.debug("Resolved cart item from response:", item);

        // If server item is missing product_name or product_price, attempt a product fallback
        const missingName = !item || !item.product_name;
        const missingPrice =
          !item || !item.product_price || Number(item.product_price) === 0;
        if ((missingName || missingPrice) && productId) {
          // Try to fetch product JSON and merge useful fields
          fetch(`/api/product/${productId}`)
            .then((r) => r.json())
            .then((pj) => {
              const prod = pj.product || pj || {};
              const fallbackItem = Object.assign({}, item);
              if (missingName && prod && prod.name)
                fallbackItem.product_name = prod.name;
              if (missingPrice && prod && (prod.price || prod.product_price))
                fallbackItem.product_price = prod.price || prod.product_price;
              if (!fallbackItem.variant_image && prod && prod.primaryImage)
                fallbackItem.variant_image = prod.primaryImage;
              console.debug("Using fallback item for popup:", fallbackItem);
              window._lastCartPopupData = {
                color: selectedColor,
                size: selectedSize,
                quantity: qty,
                item: fallbackItem,
              };
              updatePopupContent(
                selectedColor,
                selectedSize,
                qty,
                fallbackItem
              );
            })
            .catch((e) => {
              console.warn(
                "Failed to fetch product fallback after add-to-cart:",
                e
              );
              window._lastCartPopupData = {
                color: selectedColor,
                size: selectedSize,
                quantity: qty,
                item: item,
              };
              updatePopupContent(selectedColor, selectedSize, qty, item);
            });
        } else {
          // Get seller information from page data
          const sellerId = window._pageProductData?.seller_id || 
                          window._pageProductData?.sellerId ||
                          (window._pageSellerInfo && window._pageSellerInfo.id);
          
          // Add seller info to item data for modal
          const itemWithSeller = {
            ...item,
            sellerId: sellerId,
            productId: productId
          };
          
          updatePopupContent(selectedColor, selectedSize, qty, itemWithSeller);
        }

        // update cart counts
        if (
          typeof updateCartCount === "function" &&
          data.cart_count !== undefined
        ) {
          updateCartCount(data.cart_count);
        } else if (data.cart_count !== undefined) {
          const headerCount = document.querySelector(".cart-count");
          if (headerCount) headerCount.textContent = data.cart_count;
        }

        // Show success animation then modal
        if (typeof showCartSuccessAnimation === "function") {
          showCartSuccessAnimation();
        } else if (typeof openCartModal === "function") {
          openCartModal();
        }

        // success button feedback
        if (addToBagBtn) {
          const originalText = addToBagBtn.innerHTML;
          addToBagBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20,6 9,17 4,12"></polyline></svg> ADDED TO BAG`;
          addToBagBtn.style.backgroundColor = "#27ae60";
          setTimeout(() => {
            addToBagBtn.innerHTML = originalText;
            addToBagBtn.style.backgroundColor = "";
          }, 2000);
        }
      } else {
        const err = (data && data.error) || "Failed to add to cart";
        if (addToBagBtn) {
          const originalText = addToBagBtn.innerHTML;
          addToBagBtn.innerHTML = err.toUpperCase();
          addToBagBtn.style.backgroundColor = "#e74c3c";
          setTimeout(() => {
            addToBagBtn.innerHTML = originalText;
            addToBagBtn.style.backgroundColor = "";
          }, 2000);
        }
        console.warn("Add to cart failed:", data);
      }
    })
    .catch((error) => {
      console.error("Error adding to cart:", error);
      if (addToBagBtn) {
        const originalText = addToBagBtn.innerHTML;
        addToBagBtn.innerHTML = "ERROR";
        addToBagBtn.style.backgroundColor = "#e74c3c";
        setTimeout(() => {
          addToBagBtn.innerHTML = originalText;
          addToBagBtn.style.backgroundColor = "";
        }, 2000);
      }
    });
}

// Function to update popup content dynamically
function updatePopupContent(color, size, quantity, itemData) {
  // itemData is optional server-returned item object. If provided, prefer it.
  console.log("updatePopupContent called", { color, size, quantity, itemData });
  const productNameEl = document.getElementById("cartModalProductName");
  const colorEl = document.getElementById("cartModalSelectedColor");
  const sizeEl = document.getElementById("cartModalSelectedSize");
  const qtyEl = document.getElementById("cartModalSelectedQuantity");
  const priceEl = document.getElementById("cartModalProductPrice");
  const modalImg =
    document.getElementById("cartModalProductImage") ||
    document.querySelector(".cart-product-image img");

  console.debug("updatePopupContent itemData:", itemData);

  // Product name
  const productName =
    (itemData && (itemData.product_name || itemData.name || itemData.title)) ||
    document.querySelector(".product-title")?.textContent ||
    "";
  if (productNameEl) productNameEl.textContent = productName;
  // also support templates that use class selector
  const altNameEl = document.querySelector(".cart-product-name");
  if (altNameEl && altNameEl !== productNameEl)
    altNameEl.textContent = productName;

  // Color / Size / Quantity
  if (colorEl)
    colorEl.textContent = (itemData && itemData.color) || color || "";
  if (sizeEl) sizeEl.textContent = (itemData && itemData.size) || size || "";
  if (qtyEl)
    qtyEl.textContent = quantity || (itemData && itemData.quantity) || 1;
  // also update class-based quantity display if present
  const altQtyEl =
    document.querySelector(".cart-product-quantity span") ||
    document.querySelector(".cart-product-quantity");
  if (altQtyEl)
    altQtyEl.textContent = quantity || (itemData && itemData.quantity) || 1;

  // Determine SKU and base price
  let sku =
    (itemData &&
      (itemData.sku || itemData.variant_sku || itemData.variant_sku)) ||
    null;
  if (!sku) {
    // try to read from selected size button
    const selectedSizeBtn =
      document.querySelector(".size-option.active") ||
      document.querySelector('.size-option[data-size="' + size + '"]');
    if (selectedSizeBtn && selectedSizeBtn.dataset.sku)
      sku = selectedSizeBtn.dataset.sku;
  }

  // Price
  const basePrice =
    (itemData &&
      (parseFloat(
        itemData.product_price || itemData.price || itemData.unit_price
      ) ||
        0)) ||
    parseFloat(
      document.querySelector(".price-main")?.textContent.replace(/[₱,]/g, "")
    ) ||
    0;
  const qty = parseInt(quantity || (itemData && itemData.quantity) || 1);
  const subtotal = Number((basePrice * qty).toFixed(2));

  // Image - prefer itemData.variant_image, then current main image, then product primary
  let productImageSrc =
    (itemData &&
      (itemData.variant_image ||
        itemData.image_url ||
        itemData.image ||
        itemData.variant_image_url)) ||
    document.getElementById("mainImage")?.src ||
    (window._pageProductData &&
      (window._pageProductData.primaryImage ||
        window._pageProductData.primary_image)) ||
    "";

  // Guard against obviously invalid data URLs
  if (
    typeof productImageSrc === "string" &&
    productImageSrc.startsWith("data:") &&
    productImageSrc.length < 100
  ) {
    console.warn("Ignoring invalid inline image data URL for popup image");
    productImageSrc = "";
  }

  // If data seems missing (price 0 or no image), try to fetch product JSON as fallback
  const needsFallback =
    (basePrice === 0 || !productImageSrc) &&
    ((itemData && itemData.product_id) ||
      (window._pageProductData && window._pageProductData.id));
  if (needsFallback) {
    const pid =
      (itemData && itemData.product_id) ||
      (window._pageProductData && window._pageProductData.id);
    if (pid) {
      fetch(`/api/product/${pid}`)
        .then((r) => r.json())
        .then((pjson) => {
          const prod = pjson.product || pjson;
          console.log("Popup fallback product fetch", prod);
          const fallbackPrice =
            parseFloat(prod.price || prod.product_price || 0) || basePrice;
          const fallbackImage =
            (prod.variant_photos &&
              Object.values(prod.variant_photos)[0] &&
              (Object.values(prod.variant_photos)[0].primary ||
                Object.values(prod.variant_photos)[0].image)) ||
            prod.primaryImage ||
            prod.primary_image ||
            productImageSrc;

          // update computed values
          const fqty = qty;
          const fsubtotal = Number((fallbackPrice * fqty).toFixed(2));

          // update DOM
          if (priceEl)
            priceEl.textContent = `₱${Number(
              fallbackPrice
            ).toLocaleString()} · Subtotal: ₱${Number(
              fsubtotal
            ).toLocaleString()}`;
          const altPriceEl = document.querySelector(".cart-product-price");
          if (altPriceEl)
            altPriceEl.textContent = `₱${Number(
              fallbackPrice
            ).toLocaleString()}`;
          const subtotalEl =
            document.getElementById("cartModalSubtotalAmount") ||
            document.querySelector(".cart-subtotal-amount");
          if (subtotalEl)
            subtotalEl.textContent = `₱${Number(fsubtotal).toLocaleString()}`;

          if (modalImg && fallbackImage) modalImg.src = fallbackImage;
          const altModalImg =
            document.querySelector(
              "#cartModalOverlay .cart-product-image img"
            ) ||
            document.querySelector(
              ".cart-product-section .cart-product-image img"
            ) ||
            document.querySelector(".cart-product-image img");
          if (altModalImg && fallbackImage) altModalImg.src = fallbackImage;
        })
        .catch((e) =>
          console.warn("Failed to fetch product fallback for popup", e)
        );
    }
  }

  if (priceEl)
    priceEl.textContent = `₱${Number(
      basePrice || 0
    ).toLocaleString()} · Subtotal: ₱${Number(subtotal).toLocaleString()}`;

  // Update alternative price/subtotal selectors used in older template
  const altPriceEl = document.querySelector(".cart-product-price");
  if (altPriceEl)
    altPriceEl.textContent = `₱${Number(basePrice || 0).toLocaleString()}`;
  const subtotalEl =
    document.getElementById("cartModalSubtotalAmount") ||
    document.querySelector(".cart-subtotal-amount");
  if (subtotalEl)
    subtotalEl.textContent = `₱${Number(subtotal || 0).toLocaleString()}`;

  // SKU display (if present, show in modal if element exists)
  const skuEl = document.getElementById("cartModalProductSKU");
  if (skuEl) skuEl.textContent = sku || "";

  if (modalImg && productImageSrc) {
    try {
      modalImg.src = productImageSrc;
    } catch (e) {
      console.warn("Failed to set modal image src:", e);
    }
  }

  // If image element wasn't found or not updated, try alternate selectors
  if ((!modalImg || !modalImg.src) && productImageSrc) {
    const altModalImg =
      document.querySelector("#cartModalOverlay .cart-product-image img") ||
      document.querySelector(".cart-product-section .cart-product-image img") ||
      document.querySelector(".cart-product-image img");
    if (altModalImg) altModalImg.src = productImageSrc;
  }

  // Update item count display in modal header
  const itemCount = document.querySelector(".cart-item-count");
  if (itemCount && itemData && itemData.cart_count) {
    itemCount.textContent = `${itemData.cart_count} Item${
      itemData.cart_count > 1 ? "s" : ""
    }`;
  }

  // Call the new populateCartModal function if available
  if (typeof window.populateCartModal === 'function') {
    try {
      const modalData = {
        name: productName,
        price: basePrice,
        color: (itemData && itemData.color) || color || '',
        size: (itemData && itemData.size) || size || '',
        quantity: qty,
        image: productImageSrc,
        sellerId: itemData?.sellerId,
        productId: itemData?.productId || (window._pageProductData && window._pageProductData.id)
      };
      window.populateCartModal(modalData);
    } catch (e) {
      console.warn('Error calling populateCartModal:', e);
    }
  }

  // Safety fallback: sometimes modal content is rendered/overwritten by other scripts.
  // Re-check shortly after and populate from known sources if values look like defaults.
  setTimeout(() => {
    try {
      const pnameEl =
        document.getElementById("cartModalProductName") ||
        document.querySelector(".cart-product-name");
      const priceElement =
        document.getElementById("cartModalProductPrice") ||
        document.querySelector(".cart-product-price");
      const subtotalElement =
        document.getElementById("cartModalSubtotalAmount") ||
        document.querySelector(".cart-subtotal-amount");

      const currentName =
        pnameEl && (pnameEl.textContent || pnameEl.innerText || "").trim();
      const currentPrice =
        priceElement &&
        (priceElement.textContent || priceElement.innerText || "").trim();

      const looksDefaultName =
        !currentName || currentName === "Product" || currentName === "";
      const looksDefaultPrice =
        !currentPrice ||
        currentPrice.includes("₱0") ||
        currentPrice.includes("$0") ||
        currentPrice === "₱0";

      if (looksDefaultName || looksDefaultPrice) {
        console.debug(
          "Popup appears unpopulated — applying safety fallback population",
          { looksDefaultName, looksDefaultPrice }
        );

        const fallbackName =
          (itemData && (itemData.product_name || itemData.name)) ||
          window._pageProductData?.name ||
          document.querySelector(".product-title")?.textContent ||
          "";
        const fallbackPrice =
          (itemData && (itemData.product_price || itemData.price)) ||
          window._pageProductData?.price ||
          parseFloat(
            document
              .querySelector(".price-main")
              ?.textContent.replace(/[₱,]/g, "")
          ) ||
          0;
        const fallbackQty = quantity || (itemData && itemData.quantity) || 1;
        const fallbackSubtotal = Number(
          (fallbackPrice * fallbackQty).toFixed(2)
        );

        if (pnameEl && looksDefaultName)
          pnameEl.textContent = fallbackName || "";
        if (priceElement && looksDefaultPrice)
          priceElement.textContent = `₱${Number(
            fallbackPrice || 0
          ).toLocaleString()} · Subtotal: ₱${Number(
            fallbackSubtotal
          ).toLocaleString()}`;
        if (subtotalElement && looksDefaultPrice)
          subtotalElement.textContent = `₱${Number(
            fallbackSubtotal || 0
          ).toLocaleString()}`;

        // also update modal image if missing
        const modalImageEl =
          document.getElementById("cartModalProductImage") ||
          document.querySelector(".cart-product-image img");
        if (
          modalImageEl &&
          (!modalImageEl.src ||
            modalImageEl.src.endsWith("banner.png") ||
            modalImageEl.src.includes("data:"))
        ) {
          const fallbackImg =
            (itemData && (itemData.variant_image || itemData.image_url)) ||
            window._pageProductData?.primaryImage ||
            window._pageProductData?.primary_image ||
            document.getElementById("mainImage")?.src ||
            "";
          if (fallbackImg) modalImageEl.src = fallbackImg;
        }
      }
    } catch (e) {
      console.warn("Popup fallback repopulation failed", e);
    }
  }, 250);
}

// Backwards-compatible helper expected by some template code
// Some older templates call `updateQuantityControls()` after selecting a size.
// Provide a thin shim that updates the buttons and popup quantity displays.
window.updateQuantityControls = function () {
  try {
    updateQuantityButtons();

    // Also update any open modal quantity displays
    const quantityInput = document.getElementById("quantityInput");
    const currentQty = parseInt(quantityInput?.value) || 1;
    const altQtyEl =
      document.querySelector(".cart-product-quantity span") ||
      document.querySelector(".cart-product-quantity");
    const qtyEl = document.getElementById("cartModalSelectedQuantity");
    if (altQtyEl) altQtyEl.textContent = currentQty;
    if (qtyEl) qtyEl.textContent = currentQty;
  } catch (e) {
    console.warn("updateQuantityControls shim failed:", e);
  }
};

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

    // Fetch variant metadata (ids, skus, images) for later use
    try {
      fetchProductVariants(product.id).catch((e) =>
        console.warn("fetchProductVariants failed:", e)
      );
    } catch (e) {
      console.warn("Error initiating fetchProductVariants:", e);
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

// Wrap global openCartModal to refresh popup content when modal is shown
(function () {
  try {
    const _orig = window.openCartModal;
    window.openCartModal = function () {
      try {
        if (window._lastCartPopupData) {
          const d = window._lastCartPopupData;
          updatePopupContent(d.color, d.size, d.quantity, d.item);
        }
      } catch (e) {
        console.warn("Error refreshing cart modal content before open:", e);
      }
      if (typeof _orig === "function") return _orig.apply(this, arguments);
      // Fallback behavior if no original: show overlay
      const modal = document.getElementById("cartModalOverlay");
      if (modal) modal.classList.add("active");
      document.body.style.overflow = "hidden";
    };
  } catch (e) {
    console.warn("Failed to wrap openCartModal:", e);
  }
})();

// Fetch all variants for product and keep a map for quick lookup
window.fetchProductVariants = async function (productId) {
  if (!productId) return null;
  try {
    const resp = await fetch(`/api/products/${productId}/variants`);
    if (!resp.ok) {
      console.warn("fetchProductVariants non-ok response", resp.status);
      return null;
    }
    const data = await resp.json();
    if (!data || !data.variants) return null;

    // Build a map: colorName -> variant object
    const map = {};
    data.variants.forEach((v) => {
      try {
        const color = v.color_name || v.variant_name || v.color || "";
        if (!color) return;
        map[color] = {
          variant_id: v.variant_id || null,
          color_name: color,
          color_hex: v.color_hex || (v.images && v.images.color_hex) || null,
          images: v.images || [],
          sizes: Array.isArray(v.sizes) ? v.sizes : [],
        };
      } catch (e) {
        /* ignore malformed variant */
      }
    });

    window._productVariants = map;
    console.log("Loaded product variants map", map);
    return map;
  } catch (err) {
    console.warn("Error fetching product variants:", err);
    return null;
  }
};
