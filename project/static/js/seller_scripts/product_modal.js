// Product Details Modal Handler
// Handles fetching and displaying full product details in a modal

document.addEventListener("DOMContentLoaded", () => {
  console.log("[v0] Product modal handler loaded");

  // Handle View button clicks
  document.addEventListener("click", (e) => {
    if (e.target.closest(".btn-view-product")) {
      const btn = e.target.closest(".btn-view-product");
      const productId = btn.dataset.productId;

      if (!productId) {
        console.error("[v0] No product ID found");
        return;
      }

      fetchProductDetails(productId);
    }
  });

  function fetchProductDetails(productId) {
    fetch(`/seller/product/${productId}/details`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((product) => {
        console.log("[v0] Product details loaded:", product);
        openProductModal(product);
      })
      .catch((error) => {
        console.error("[v0] Error fetching product details:", error);
        alert("Error loading product details. Please try again.");
      });
  }

  function openProductModal(product) {
    const modal = createProductModal(product);
    document.body.appendChild(modal);

    // Show modal
    modal.classList.add("show");

    // Close button handler
    const closeBtn = modal.querySelector(".modal-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        modal.classList.remove("show");
        setTimeout(() => {
          document.body.removeChild(modal);
        }, 300);
      });
    }

    // Close on background click
    modal.addEventListener("click", function (e) {
      if (e.target === this) {
        this.classList.remove("show");
        setTimeout(() => {
          document.body.removeChild(modal);
        }, 300);
      }
    });
  }

  function createProductModal(product) {
    const variantsHtml =
      product.variants.length > 0
        ? product.variants
            .map(
              (v) => `
        <tr>
          <td>${v.sku || "-"}</td>
          <td>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span>${v.color || "-"}</span>
              ${
                v.colorHex
                  ? `<div style="width: 24px; height: 24px; background-color: ${v.colorHex}; border: 1px solid #ccc; border-radius: 4px;"></div>`
                  : ""
              }
            </div>
          </td>
          <td>${v.size || "-"}</td>
          <td style="text-align: center; font-weight: 600;">${v.stock || 0}</td>
          <td style="text-align: center;">${v.lowStock || 0}</td>
        </tr>
      `
            )
            .join("")
        : '<tr><td colspan="5" style="text-align: center; color: #999;">No variants</td></tr>';

    const discountInfo = product.discount_type
      ? `${
          product.discount_type === "percentage"
            ? product.discount_value + "%"
            : "₱" + product.discount_value
        }`
      : "None";

    const subitems = product.attributes?.subitems || [];
    const subitemHtml =
      subitems.length > 0
        ? subitems
            .map(
              (item) =>
                `<span style="display: inline-block; background: #f0f0f0; padding: 4px 8px; border-radius: 4px; margin-right: 8px; margin-bottom: 4px;">${item}</span>`
            )
            .join("")
        : '<span style="color: #999;">-</span>';

    const modal = document.createElement("div");
    modal.className = "product-modal-overlay";
    modal.innerHTML = `
      <div class="product-modal-content">
        <div class="modal-header">
          <h2>${product.name}</h2>
          <button type="button" class="modal-close" aria-label="Close">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="modal-section">
            <h3>Basic Information</h3>
            <div class="info-grid">
              <div><strong>Category:</strong> ${product.category}</div>
              <div><strong>Subcategory:</strong> ${
                product.subcategory || "-"
              }</div>
              <div><strong>Price:</strong> ₱${product.price.toFixed(2)}</div>
              <div><strong>Compare At:</strong> ${
                product.compare_at_price
                  ? "₱" + product.compare_at_price.toFixed(2)
                  : "-"
              }</div>
              <div><strong>Discount:</strong> ${discountInfo}</div>
              <div><strong>Voucher Type:</strong> ${
                product.voucher_type || "-"
              }</div>
            </div>
          </div>
          
          <div class="modal-section">
            <h3>Description</h3>
            <p>${product.description || "-"}</p>
          </div>
          
          <div class="modal-section">
            <h3>Materials & Care</h3>
            <p>${product.materials || "-"}</p>
          </div>
          
          <div class="modal-section">
            <h3>Details & Fit</h3>
            <p>${product.details_fit || "-"}</p>
          </div>
          
          <div class="modal-section">
            <h3>Sub-Items</h3>
            <div>${subitemHtml}</div>
          </div>
          
          <div class="modal-section">
            <h3>Inventory</h3>
            <div class="info-grid">
              <div><strong>Total Stock:</strong> ${product.total_stock}</div>
              <div><strong>Low Stock Threshold:</strong> ${
                product.low_stock_threshold
              }</div>
            </div>
          </div>
          
          <div class="modal-section">
            <h3>Variants</h3>
            <table class="variants-table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Color</th>
                  <th>Size</th>
                  <th>Stock</th>
                  <th>Low Stock</th>
                </tr>
              </thead>
              <tbody>
                ${variantsHtml}
              </tbody>
            </table>
          </div>
          
          ${
            product.primary_image
              ? `
          <div class="modal-section">
            <h3>Product Image</h3>
            <img src="${product.primary_image}" alt="${product.name}" style="max-width: 100%; height: auto; max-height: 300px;">
          </div>
          `
              : ""
          }
        </div>
      </div>
    `;

    return modal;
  }
});
