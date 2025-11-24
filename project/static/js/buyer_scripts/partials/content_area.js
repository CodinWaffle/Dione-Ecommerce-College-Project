// Content Area JavaScript - Shared functionality for all filter pages
// This handles product grid, sorting, and pagination

let activeFilters = {};
let totalProducts = 24;
let displayedProducts = 12;
let currentPage = 1;
let totalPages = Math.ceil(totalProducts / displayedProducts);

function updateProductCount() {
  const productCountElement = document.getElementById("productCount");
  const viewMoreElement = document.getElementById("viewMore");
  const totalProductsElement = document.getElementById("totalProducts");
  const emptyState = document.getElementById("emptyState");
  const productGrid = document.getElementById("productGrid");
  const paginationContainer = document.querySelector(".pagination-container");

  // Calculate filtered products based on active filters
  let filteredCount = totalProducts;
  if (Object.keys(activeFilters).length > 0) {
    filteredCount = Math.floor(totalProducts * 0.6);
  }

  // If the DOM product grid exists, prefer its actual product-card count when available
  if (productGrid) {
    const domCount = productGrid.querySelectorAll(".product-card").length;
    if (typeof domCount === "number") {
      // If DOM has zero product cards, treat as empty regardless of totalProducts
      if (domCount === 0) filteredCount = 0;
      // If DOM count differs and is more realistic use it
      if (domCount > 0 && domCount !== totalProducts) filteredCount = domCount;
    }
  }

  // Update total pages based on filtered results (ensure at least 1 to avoid divide by zero)
  totalPages = Math.max(1, Math.ceil(filteredCount / displayedProducts));

  // Handle empty state
  if (filteredCount === 0) {
    if (productCountElement) productCountElement.textContent = "0";
    if (totalProductsElement) totalProductsElement.textContent = "0";
    if (viewMoreElement) viewMoreElement.style.display = "none";
    if (emptyState) emptyState.style.display = "flex";
    if (productGrid) productGrid.style.display = "none";
    if (paginationContainer) paginationContainer.style.display = "none";
    // Ensure pagination shows 0-0
    currentPage = 1;
  } else {
    if (emptyState) emptyState.style.display = "none";
    if (productGrid) productGrid.style.display = "grid";
    if (productCountElement) {
      productCountElement.textContent = Math.min(
        displayedProducts,
        filteredCount
      );
    }
    if (totalProductsElement) {
      totalProductsElement.textContent = filteredCount;
    }
    if (viewMoreElement) {
      viewMoreElement.style.display =
        filteredCount > displayedProducts ? "inline" : "none";
    }
    if (paginationContainer) paginationContainer.style.display = "flex";
  }

  updatePagination();
}

function updatePagination() {
  const currentRangeElement = document.getElementById("currentRange");
  const totalItemsElement = document.getElementById("totalItems");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const pageNumbers = document.getElementById("pageNumbers");

  // Calculate filtered products
  let filteredCount = totalProducts;
  if (Object.keys(activeFilters).length > 0) {
    filteredCount = Math.floor(totalProducts * 0.6);
  }

  // Prefer DOM count if product grid exists (keeps display consistent)
  if (document.getElementById("productGrid")) {
    const domCount = document
      .getElementById("productGrid")
      .querySelectorAll(".product-card").length;
    if (typeof domCount === "number") filteredCount = domCount;
  }

  // Update range display
  if (filteredCount === 0) {
    if (currentRangeElement) {
      currentRangeElement.textContent = "0-0";
    }
    if (totalItemsElement) {
      totalItemsElement.textContent = "0";
    }
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = true;
    if (pageNumbers) pageNumbers.innerHTML = "";
    return;
  }

  const startItem = (currentPage - 1) * displayedProducts + 1;
  const endItem = Math.min(currentPage * displayedProducts, filteredCount);
  if (currentRangeElement) {
    currentRangeElement.textContent = `${startItem}-${endItem}`;
  }
  if (totalItemsElement) {
    totalItemsElement.textContent = filteredCount;
  }

  // Update prev/next buttons
  if (prevBtn) {
    prevBtn.disabled = currentPage === 1;
  }
  if (nextBtn) {
    nextBtn.disabled = currentPage === totalPages;
  }

  // Generate page numbers
  if (pageNumbers) {
    generatePageNumbers(pageNumbers);
  }
}

function generatePageNumbers(container) {
  container.innerHTML = "";

  const maxVisiblePages = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

  // Adjust start if we're near the end
  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  // Add first page if not visible
  if (startPage > 1) {
    container.appendChild(createPageButton(1));
    if (startPage > 2) {
      const ellipsis = document.createElement("span");
      ellipsis.className = "page-ellipsis";
      ellipsis.textContent = "...";
      container.appendChild(ellipsis);
    }
  }

  // Add visible page numbers
  for (let i = startPage; i <= endPage; i++) {
    container.appendChild(createPageButton(i));
  }

  // Add last page if not visible
  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      const ellipsis = document.createElement("span");
      ellipsis.className = "page-ellipsis";
      ellipsis.textContent = "...";
      container.appendChild(ellipsis);
    }
    container.appendChild(createPageButton(totalPages));
  }
}

function createPageButton(pageNum) {
  const button = document.createElement("button");
  button.className = `page-btn ${pageNum === currentPage ? "active" : ""}`;
  button.textContent = pageNum;
  button.dataset.page = pageNum;
  button.addEventListener("click", () => goToPage(pageNum));
  return button;
}

function goToPage(page) {
  if (page < 1 || page > totalPages) return;

  currentPage = page;
  updatePagination();

  // Scroll to top of content area
  const contentArea = document.querySelector(".content-area");
  if (contentArea) {
    contentArea.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }
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
  updateProductCount();
}

function selectColor(swatch, colorName) {
  swatch.classList.toggle("selected");
  const isSelected = swatch.classList.contains("selected");
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

function sortProducts(sortBy) {
  const productGrid = document.getElementById("productGrid");
  const products = Array.from(productGrid.children);

  products.sort((a, b) => {
    const priceA = Number.parseFloat(
      a.querySelector(".product-price")?.textContent.replace("₱", "") || 0
    );
    const priceB = Number.parseFloat(
      b.querySelector(".product-price")?.textContent.replace("₱", "") || 0
    );
    const nameA = a.querySelector(".product-name")?.textContent || "";
    const nameB = b.querySelector(".product-name")?.textContent || "";

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
      if (this.value !== "sort-by") {
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
