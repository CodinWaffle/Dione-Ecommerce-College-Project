// Preview script: read stored form data and populate the preview DOM

function getFormData(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    console.warn("Failed to parse localStorage", key, e);
    return null;
  }
}

function generateImagePreviews(images) {
  if (!images || !images.length) {
    return `
      <div class="preview-image-box">Product Image 1</div>
      <div class="preview-image-box">Product Image 2</div>
      <div class="preview-image-box">Product Image 3</div>
      <div class="preview-image-box">Product Image 4</div>
    `;
  }
  return images
    .map(
      (image, i) => `
      <div class="preview-image-box" data-image="${image}">
        ${
          image
            ? `<img src="${image}" alt="Product ${i + 1}">`
            : `Product Image ${i + 1}`
        }
      </div>
    `
    )
    .join("");
}

function generateFilterPreviews(filters) {
  if (!filters) return "";
  return Object.entries(filters)
    .map(
      ([k, v]) => `
      <div class="filter-category">
        <span class="filter-category-name">${k}:</span>
        <span class="filter-values">${
          Array.isArray(v) ? v.join(", ") : v
        }</span>
      </div>
    `
    )
    .join("");
}

function generateVariationPreviews(variations) {
  if (!variations || !variations.length) return "";
  return variations
    .map(
      (v) => `
      <div class="variation-item">
        ${Object.entries(v)
          .map(
            ([k, val]) => `<span class="variation-detail">${k}: ${val}</span>`
          )
          .join(" ")}
      </div>
    `
    )
    .join("");
}

function addImagePreviewHandlers() {
  document.querySelectorAll(".preview-image-box[data-image]").forEach((box) => {
    box.addEventListener("click", () => {
      const img = box.dataset.image;
      if (img) showLightbox(img);
    });
  });
}

function showLightbox(src) {
  const lightbox = document.createElement("div");
  lightbox.className = "preview-lightbox";
  lightbox.innerHTML = `
    <div class="lightbox-content">
      <img src="${src}" alt="Product Preview">
      <button class="close-lightbox">&times;</button>
    </div>
  `;
  document.body.appendChild(lightbox);
  lightbox.addEventListener("click", (e) => {
    if (
      e.target === lightbox ||
      e.target.classList.contains("close-lightbox")
    ) {
      document.body.removeChild(lightbox);
    }
  });
}

function setText(id, value, formatter) {
  const el = document.getElementById(id);
  if (!el) return;
  const v =
    typeof formatter === "function"
      ? formatter(value)
      : value == null || value === ""
      ? "-"
      : value;
  if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") el.value = v;
  else el.textContent = v;
}

function updatePreview() {
  const basicInfo = getFormData("productForm") || {};
  const description = getFormData("productDescriptionForm") || {};
  const stock = getFormData("productStocksForm") || {};

  // Basic fields (defensive: only set if element exists)
  setText("previewProductName", basicInfo.productName);
  setText("previewCategory", basicInfo.category);
  setText("previewSubCategory", basicInfo.subcategory);
  setText("previewSubItems", basicInfo.subitem);
  setText("previewModelInfo", basicInfo.brand || basicInfo.model);
  setText("previewPrice", basicInfo.price, (v) => (v ? `₱${v}` : "-"));
  setText("previewDiscountPercent", basicInfo.discountPercent);
  setText("previewDiscountType", basicInfo.discountType);
  setText("previewVoucherType", basicInfo.voucherType);

  // Images
  const imagesContainer = document.getElementById("previewImages");
  if (imagesContainer) {
    imagesContainer.innerHTML = generateImagePreviews(basicInfo.images || []);
    addImagePreviewHandlers();
  }

  // Filters
  const filtersContainer = document.getElementById("previewProductFilters");
  if (filtersContainer) {
    // Combine filter objects and explicit category-like fields from all steps
    const parts = [];
    if (basicInfo.filters)
      parts.push(generateFilterPreviews(basicInfo.filters));

    const collectCategoryParts = (obj) => {
      if (!obj) return;
      if (obj.category)
        parts.push(
          `<div class="filter-category"><span class="filter-category-name">Category:</span> <span class="filter-values">${obj.category}</span></div>`
        );
      if (obj.subcategory)
        parts.push(
          `<div class="filter-category"><span class="filter-category-name">Sub Category:</span> <span class="filter-values">${obj.subcategory}</span></div>`
        );
      if (obj.subitem)
        parts.push(
          `<div class="filter-category"><span class="filter-category-name">Sub-items:</span> <span class="filter-values">${obj.subitem}</span></div>`
        );
      if (obj.categories && Array.isArray(obj.categories))
        parts.push(
          `<div class="filter-category"><span class="filter-category-name">Categories:</span> <span class="filter-values">${obj.categories.join(
            ", "
          )}</span></div>`
        );
    };

    collectCategoryParts(basicInfo);
    collectCategoryParts(description);
    collectCategoryParts(stock);

    filtersContainer.innerHTML = parts.length ? parts.join("") : "-";
  }

  // Description
  setText("previewDescription", description.description);
  setText("previewMaterials", description.materials);
  setText("previewDetailsFit", description.detailsFit);

  // Stock
  setText("previewSKU", stock.sku);
  setText("previewTotalStock", stock.totalStock);

  const previewVariants = document.getElementById("previewVariants");
  if (previewVariants) {
    if (stock.variants && Array.isArray(stock.variants)) {
      previewVariants.innerHTML = stock.variants
        .map(
          (v) => `
        <div class="variant-item">
          <div>${v.sku || ""} ${v.color ? " / " + v.color : ""} ${
            v.size ? " / " + v.size : ""
          }</div>
          <div class="stock-count">${v.stock ?? 0}</div>
        </div>
      `
        )
        .join("");
    } else {
      previewVariants.innerHTML = "-";
    }
  }
}

// Run on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", updatePreview);
} else {
  updatePreview();
}

// When Add Product is clicked: save to localStorage 'products' and redirect to product management
(function () {
  function safeParse(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || "null");
    } catch (e) {
      return null;
    }
  }

  const submitBtn = document.getElementById("submitBtn");
  if (!submitBtn) return;
  submitBtn.addEventListener("click", function () {
    const basicInfo = safeParse("productForm") || {};
    const description = safeParse("productDescriptionForm") || {};
    const stock = safeParse("productStocksForm") || {};

    // Build product object for the management list (keep full details inside object)
    const products = JSON.parse(localStorage.getItem("products") || "[]");
    const nextId =
      (products.reduce((m, p) => Math.max(m, Number(p.id || 0)), 0) || 0) + 1;

    const product = {
      id: nextId,
      name:
        basicInfo.productName || description.productName || "Untitled Product",
      image:
        (basicInfo.images && basicInfo.images[0]) ||
        (description.images && description.images[0]) ||
        "/static/images/placeholder.svg",
      price: Number(basicInfo.price) || 0,
      stock:
        Number(stock.totalStock) ||
        (stock.variants
          ? stock.variants.reduce((s, v) => s + (Number(v.stock) || 0), 0)
          : 0),
      status: "active",
      category:
        basicInfo.category ||
        description.category ||
        stock.category ||
        "Uncategorized",
      sku: stock.sku || basicInfo.sku || "",
      // store full payload for preview/details modal
      _full: {
        basicInfo: basicInfo,
        description: description,
        stock: stock,
      },
      variants: stock.variants || [],
    };

    products.push(product);
    localStorage.setItem("products", JSON.stringify(products));

    // Clear draft forms
    try {
      localStorage.removeItem("productForm");
      localStorage.removeItem("productDescriptionForm");
      localStorage.removeItem("productStocksForm");
    } catch (e) {
      console.warn("Failed to clear draft after add", e);
    }

    // Redirect to product management page where the list reads from localStorage
    window.location.href = "/seller/products";
  });
})();
