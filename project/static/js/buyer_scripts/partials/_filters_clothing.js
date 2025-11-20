// JS for filters_clothing.html

let activeFilters = {};
const totalProducts = 24;
const displayedProducts = 12;
const currentPage = 1;
const totalPages = Math.ceil(totalProducts / displayedProducts);

function toggleDropdown(header) {
  const section = header.parentElement;
  section.classList.toggle("active");
}

function resetAllFilters() {
  // Clear active filters
  activeFilters = {};

  // Reset all checkboxes
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });

  // Reset color swatches
  const colorOptions = document.querySelectorAll(".color-option-item");
  colorOptions.forEach((item) => {
    item.classList.remove("selected");
  });

  // Reset price inputs
  const minPrice = document.getElementById("minPrice");
  const maxPrice = document.getElementById("maxPrice");
  if (minPrice) minPrice.value = "";
  if (maxPrice) maxPrice.value = "";

  // Update display
  updateSelectedFilters();
  updateProductCount();
}

function updateProductCount() {
  const productCountElement = document.getElementById("productCount");
  const viewMoreElement = document.getElementById("viewMore");
  const totalProductsElement = document.getElementById("totalProducts");

  // Calculate filtered products based on active filters
  let filteredCount = totalProducts;
  if (Object.keys(activeFilters).length > 0) {
    filteredCount = Math.floor(totalProducts * 0.6);
  }

  productCountElement.textContent = Math.min(displayedProducts, filteredCount);
  totalProductsElement.textContent = filteredCount;
}

function updateFilter(category, value, isChecked) {
  if (!activeFilters[category]) {
    activeFilters[category] = [];
  }

  if (isChecked) {
    if (!activeFilters[category].includes(value)) {
      activeFilters[category].push(value);
    }
  } else {
    activeFilters[category] = activeFilters[category].filter(
      (item) => item !== value
    );
    if (activeFilters[category].length === 0) {
      delete activeFilters[category];
    }
  }

  updateSelectedFilters();
}

function selectColor(element, colorName) {
  element.classList.toggle("selected");
  const isSelected = element.classList.contains("selected");
  updateFilter("color", colorName, isSelected);
}

function updateSelectedFilters() {
  const container = document.getElementById("selectedFilters");
  const resetBtn = document.getElementById("resetFiltersBtn");

  // Clear existing filter tags but keep the reset button
  const filterTags = container.querySelectorAll(".filter-tag");
  filterTags.forEach((tag) => tag.remove());

  let hasFilters = false;
  Object.keys(activeFilters).forEach((category) => {
    activeFilters[category].forEach((value) => {
      const tag = document.createElement("div");
      tag.className = "filter-tag";
      tag.innerHTML = `
                ${value}
                <span class="remove" onclick="removeFilter('${category}', '${value}')">&times;</span>
            `;
      container.insertBefore(tag, resetBtn);
      hasFilters = true;
    });
  });

  // Show/hide reset button
  if (resetBtn) {
    resetBtn.style.display = hasFilters ? "flex" : "none";
  }

  updateProductCount();
}

function removeFilter(category, value) {
  if (activeFilters[category]) {
    activeFilters[category] = activeFilters[category].filter(
      (item) => item !== value
    );
    if (activeFilters[category].length === 0) {
      delete activeFilters[category];
    }
  }

  // Uncheck the corresponding checkbox/swatch
  const checkbox = document.querySelector(`input[onchange*="${value}"]`);
  if (checkbox) {
    checkbox.checked = false;
  }

  if (category === "color") {
    document.querySelectorAll(".color-option-item").forEach((item) => {
      if (item.textContent.includes(value)) {
        item.classList.remove("selected");
      }
    });
  }

  updateSelectedFilters();
}

function sortProducts(sortBy) {
  const productGrid = document.getElementById("productGrid");
  const products = Array.from(productGrid.children);

  products.sort((a, b) => {
    const priceA = Number.parseFloat(
      a.querySelector(".product-price").textContent.replace("₱", "")
    );
    const priceB = Number.parseFloat(
      b.querySelector(".product-price").textContent.replace("₱", "")
    );
    const nameA = a.querySelector(".product-name").textContent;
    const nameB = b.querySelector(".product-name").textContent;

    switch (sortBy) {
      case "price-low":
        return priceA - priceB;
      case "price-high":
        return priceB - priceA;
      case "name-az":
        return nameA.localeCompare(nameB);
      case "name-za":
        return nameB.localeCompare(nameA);
      case "rating":
        return Math.random() - 0.5;
      case "newest":
        return Math.random() - 0.5;
      default:
        return 0;
    }
  });

  // Clear and re-append sorted products
  productGrid.innerHTML = "";
  products.forEach((product) => productGrid.appendChild(product));
}

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  updateProductCount();

  // Add sort functionality
  const sortSelect = document.getElementById("sortBy");
  if (sortSelect) {
    sortSelect.addEventListener("change", function () {
      if (this.value !== "default") {
        sortProducts(this.value);
      }
    });
  }

  // Price filter listeners
  document.getElementById("minPrice")?.addEventListener("change", function () {
    const min = this.value;
    if (min) {
      updateFilter("price", `From ₱${min}`, true);
    }
  });

  document.getElementById("maxPrice")?.addEventListener("change", function () {
    const max = this.value;
    if (max) {
      updateFilter("price", `Up to ₱${max}`, true);
    }
  });
});
