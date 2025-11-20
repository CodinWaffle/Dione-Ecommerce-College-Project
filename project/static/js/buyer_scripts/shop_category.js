/* Shop Category Page JavaScript */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize page functionality
  initFilters();
  initSorting();
  initPagination();
  console.log("Shop category page initialized");
});

// Filter functionality
function initFilters() {
  const applyBtn = document.querySelector(".btn-apply-filters");
  const clearBtn = document.querySelector(".btn-clear-filters");

  if (applyBtn) {
    applyBtn.addEventListener("click", applyFilters);
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", clearFilters);
  }

  // Color swatch selection
  const colorSwatches = document.querySelectorAll(".color-swatch");
  colorSwatches.forEach((swatch) => {
    swatch.addEventListener("click", function () {
      this.classList.toggle("selected");
    });
  });
}

function applyFilters() {
  // Get filter values
  const minPrice = document.getElementById("minPrice")?.value;
  const maxPrice = document.getElementById("maxPrice")?.value;

  const selectedSizes = Array.from(
    document.querySelectorAll(".size-options input:checked")
  ).map((cb) => cb.value);

  const selectedColors = Array.from(
    document.querySelectorAll(".color-swatch.selected")
  ).map((swatch) => swatch.dataset.color);

  const selectedBrands = Array.from(
    document.querySelectorAll(".brand-options input:checked")
  ).map((cb) => cb.value);

  console.log("Applying filters:", {
    priceRange: { min: minPrice, max: maxPrice },
    sizes: selectedSizes,
    colors: selectedColors,
    brands: selectedBrands,
  });

  // TODO: Send filter request to backend and update products
  filterProducts({
    minPrice,
    maxPrice,
    sizes: selectedSizes,
    colors: selectedColors,
    brands: selectedBrands,
  });
}

function clearFilters() {
  // Clear all filter inputs
  document.getElementById("minPrice").value = "";
  document.getElementById("maxPrice").value = "";

  document
    .querySelectorAll(".size-options input")
    .forEach((cb) => (cb.checked = false));
  document
    .querySelectorAll(".color-swatch")
    .forEach((swatch) => swatch.classList.remove("selected"));
  document
    .querySelectorAll(".brand-options input")
    .forEach((cb) => (cb.checked = false));

  // Reload all products
  filterProducts({});
}

function filterProducts(filters) {
  // TODO: Implement AJAX call to backend
  // For now, just hide/show products based on filters
  const products = document.querySelectorAll(".product-card");
  let visibleCount = 0;

  products.forEach((product) => {
    // Simple show/hide logic - replace with actual filtering
    product.style.display = "block";
    visibleCount++;
  });

  // Update product count
  const countElement = document.getElementById("productCount");
  if (countElement) {
    countElement.textContent = visibleCount;
  }
}

// Sorting functionality
function initSorting() {
  const sortSelect = document.getElementById("sortBy");

  if (sortSelect) {
    sortSelect.addEventListener("change", function () {
      sortProducts(this.value);
    });
  }
}

function sortProducts(sortBy) {
  console.log("Sorting products by:", sortBy);

  const productsGrid = document.getElementById("productsGrid");
  const products = Array.from(productsGrid.querySelectorAll(".product-card"));

  // TODO: Implement actual sorting logic based on sortBy value
  // For now, just log the selection

  switch (sortBy) {
    case "price-low":
      // Sort by price ascending
      break;
    case "price-high":
      // Sort by price descending
      break;
    case "newest":
      // Sort by date
      break;
    case "popular":
      // Sort by popularity
      break;
    default:
      // Featured/default sorting
      break;
  }
}

// Pagination functionality
function initPagination() {
  const pageButtons = document.querySelectorAll(".page-btn:not(:disabled)");

  pageButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const pageNum = this.textContent.trim();

      if (pageNum === "<" || pageNum === ">") {
        // Handle previous/next
        console.log("Navigate:", pageNum === "<" ? "previous" : "next");
      } else {
        // Handle specific page
        changePage(parseInt(pageNum));
      }
    });
  });
}

function changePage(pageNum) {
  console.log("Changing to page:", pageNum);

  // Update active state
  document.querySelectorAll(".page-btn").forEach((btn) => {
    btn.classList.remove("active");
    if (btn.textContent.trim() === pageNum.toString()) {
      btn.classList.add("active");
    }
  });

  // Scroll to top
  window.scrollTo({ top: 0, behavior: "smooth" });

  // TODO: Load products for selected page
}

// Add to cart functionality
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("btn-add-cart")) {
    const productId = e.target.dataset.productId;
    addToCart(productId);
  }
});

function addToCart(productId) {
  console.log("Adding product to cart:", productId);

  // TODO: Implement add to cart logic
  // Show success message
  alert("Product added to cart!");
}
