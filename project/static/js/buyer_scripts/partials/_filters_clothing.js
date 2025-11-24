// JS for filters_clothing.html - wrapper that uses shared content area functions

function toggleDropdown(header) {
  const section = header.closest(".filter-section");
  if (section) {
    section.classList.toggle("active");
  }
}

// Initialize page: use shared functions from content_area.js when available
document.addEventListener("DOMContentLoaded", () => {
  if (typeof updateProductCount === "function") {
    updateProductCount();
  }

  // Add sort functionality (delegates to shared sortProducts)
  const sortSelect = document.getElementById("sortBy");
  if (sortSelect) {
    sortSelect.addEventListener("change", function () {
      if (
        this.value &&
        this.value !== "sort-by" &&
        typeof sortProducts === "function"
      ) {
        sortProducts(this.value);
      }
    });
  }

  // Price filter listeners delegate to shared updateFilter
  document.getElementById("minPrice")?.addEventListener("change", function () {
    const min = this.value;
    if (min && typeof updateFilter === "function") {
      updateFilter("price", `From ₱${min}`, true);
    }
  });

  document.getElementById("maxPrice")?.addEventListener("change", function () {
    const max = this.value;
    if (max && typeof updateFilter === "function") {
      updateFilter("price", `Up to ₱${max}`, true);
    }
  });
});
