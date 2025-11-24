// JS for _filters_shoes.html - wrapper that uses shared content area functions

function toggleDropdown(header) {
  const section = header.closest(".filter-section");
  if (section) {
    section.classList.toggle("active");
  }
}

// Initialize page: delegate behavior to shared functions in content_area.js
document.addEventListener("DOMContentLoaded", function () {
  if (typeof updateProductCount === "function") updateProductCount();

  // Pagination buttons (if needed) will be handled by shared functions
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  if (prevBtn) {
    prevBtn.addEventListener("click", function () {
      if (typeof goToPage === "function")
        goToPage((window.currentPage || 1) - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      if (typeof goToPage === "function")
        goToPage((window.currentPage || 1) + 1);
    });
  }

  // Initialize sort dropdown
  const sortDropdown = document.getElementById("sortBy");
  if (sortDropdown) {
    sortDropdown.addEventListener("change", function () {
      if (this.value && typeof sortProducts === "function")
        sortProducts(this.value);
    });
  }

  // Attach programmatic listeners as a fallback for collapsible headers
  document.querySelectorAll(".filter-header").forEach((btn) => {
    if (!btn.dataset.listenerAttached) {
      btn.addEventListener("click", function () {
        const section = btn.closest(".filter-section");
        if (section) section.classList.toggle("active");
      });
      btn.dataset.listenerAttached = "true";
    }
  });

  // Price inputs delegate to shared updateFilter
  const minPriceInput = document.getElementById("minPrice");
  const maxPriceInput = document.getElementById("maxPrice");

  if (minPriceInput) {
    minPriceInput.addEventListener("change", function () {
      const min = this.value;
      if (min && typeof updateFilter === "function")
        updateFilter("price", `From ₱${min}`, true);
    });
  }

  if (maxPriceInput) {
    maxPriceInput.addEventListener("change", function () {
      const max = this.value;
      if (max && typeof updateFilter === "function")
        updateFilter("price", `Up to ₱${max}`, true);
    });
  }
});
