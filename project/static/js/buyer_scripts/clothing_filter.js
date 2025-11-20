/* Clothing-specific filter functionality */

console.log("Clothing filter module loaded");

// Initialize clothing-specific filter behaviors when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  initClothingFilters();
});

function initClothingFilters() {
  // Enhanced size filter handling for clothing
  initSizeSelectionUI();

  // Enhanced color swatch interactions
  initColorSwatchAnimations();

  // Live filter updates
  attachLiveFilterListeners();

  // Load saved filters if any
  loadSavedFilters();
}

// Initialize size selection UI with better interactions
function initSizeSelectionUI() {
  const sizeOptions = document.querySelectorAll(".size-options input");

  sizeOptions.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const label = this.parentElement;
      if (this.checked) {
        label.classList.add("selected");
      } else {
        label.classList.remove("selected");
      }
      updateFilterSummary();
    });
  });
}

// Initialize color swatch animations and selection
function initColorSwatchAnimations() {
  const colorSwatches = document.querySelectorAll(".color-swatch");

  colorSwatches.forEach((swatch) => {
    // Click to select/deselect
    swatch.addEventListener("click", function (e) {
      e.preventDefault();
      this.classList.toggle("selected");
      updateFilterSummary();
    });

    // Add aria labels for accessibility
    const color = this.dataset.color || "unknown";
    swatch.setAttribute("aria-label", `Select ${color} color`);
    swatch.setAttribute("role", "checkbox");
  });
}

// Attach live filter listeners
function attachLiveFilterListeners() {
  // Price range inputs
  const minPrice = document.getElementById("minPrice");
  const maxPrice = document.getElementById("maxPrice");

  if (minPrice) {
    minPrice.addEventListener("input", function () {
      validatePriceInputs(this, maxPrice);
      updateFilterSummary();
    });
  }

  if (maxPrice) {
    maxPrice.addEventListener("input", function () {
      validatePriceInputs(minPrice, this);
      updateFilterSummary();
    });
  }

  // Brand options
  const brandOptions = document.querySelectorAll(".brand-options input");
  brandOptions.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      updateFilterSummary();
    });
  });
}

// Validate price inputs
function validatePriceInputs(minInput, maxInput) {
  if (!minInput || !maxInput) return;

  const minVal = parseFloat(minInput.value) || 0;
  const maxVal = parseFloat(maxInput.value) || 0;

  if (minVal > maxVal && maxVal > 0) {
    minInput.value = maxVal;
  }
  if (maxVal < minVal && minVal > 0) {
    maxInput.value = minVal;
  }
}

// Update filter summary display
function updateFilterSummary() {
  const selectedSizes = Array.from(
    document.querySelectorAll(".size-options input:checked")
  ).length;

  const selectedColors = document.querySelectorAll(
    ".color-swatch.selected"
  ).length;

  const selectedBrands = Array.from(
    document.querySelectorAll(".brand-options input:checked")
  ).length;

  const minPrice = document.getElementById("minPrice")?.value || "";
  const maxPrice = document.getElementById("maxPrice")?.value || "";

  // Log current filter state (for debugging)
  console.log("Current filters:", {
    sizes: selectedSizes,
    colors: selectedColors,
    brands: selectedBrands,
    priceRange: minPrice && maxPrice ? `${minPrice}-${maxPrice}` : "any",
  });
}

// Load previously saved filters
function loadSavedFilters() {
  const savedFilters = localStorage.getItem("clothingFilters");
  if (savedFilters) {
    try {
      const filters = JSON.parse(savedFilters);
      restoreFilters(filters);
    } catch (e) {
      console.warn("Could not restore saved filters:", e);
    }
  }
}

// Restore filters from saved state
function restoreFilters(filters) {
  if (filters.minPrice) {
    const minInput = document.getElementById("minPrice");
    if (minInput) minInput.value = filters.minPrice;
  }

  if (filters.maxPrice) {
    const maxInput = document.getElementById("maxPrice");
    if (maxInput) maxInput.value = filters.maxPrice;
  }

  if (filters.sizes && filters.sizes.length > 0) {
    filters.sizes.forEach((size) => {
      const checkbox = document.querySelector(
        `.size-options input[value="${size}"]`
      );
      if (checkbox) {
        checkbox.checked = true;
        checkbox.parentElement.classList.add("selected");
      }
    });
  }

  if (filters.colors && filters.colors.length > 0) {
    filters.colors.forEach((color) => {
      const swatch = document.querySelector(
        `.color-swatch[data-color="${color}"]`
      );
      if (swatch) {
        swatch.classList.add("selected");
      }
    });
  }

  if (filters.brands && filters.brands.length > 0) {
    filters.brands.forEach((brand) => {
      const checkbox = document.querySelector(
        `.brand-options input[value="${brand}"]`
      );
      if (checkbox) {
        checkbox.checked = true;
      }
    });
  }
}

// Save current filters to localStorage
function saveCurrentFilters() {
  const filters = {
    minPrice: document.getElementById("minPrice")?.value || "",
    maxPrice: document.getElementById("maxPrice")?.value || "",
    sizes: Array.from(
      document.querySelectorAll(".size-options input:checked")
    ).map((cb) => cb.value),
    colors: Array.from(document.querySelectorAll(".color-swatch.selected")).map(
      (swatch) => swatch.dataset.color
    ),
    brands: Array.from(
      document.querySelectorAll(".brand-options input:checked")
    ).map((cb) => cb.value),
  };

  localStorage.setItem("clothingFilters", JSON.stringify(filters));
}

// Override the clearFilters function for clothing-specific behavior
if (typeof window.clearFilters === "function") {
  const originalClearFilters = window.clearFilters;
  window.clearFilters = function () {
    originalClearFilters();
    localStorage.removeItem("clothingFilters");
    console.log("Clothing filters cleared");
  };
}
