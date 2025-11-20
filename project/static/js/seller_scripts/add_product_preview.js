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
      <div class="preview-image-box">Main Photo</div>
      <div class="preview-image-box">Product Photo</div>
    `;
  }
  return images
    .map(
      (image, i) => `
      <div class="preview-image-box" data-image="${image}">
        ${
          image
            ? `<img src="${image}" alt="Product ${i + 1}">`
            : `${i === 0 ? "Main Photo" : "Product Photo"}`
        }
      </div>
    `
    )
    .join("");
}

function generateGalleryPreviews(images, label) {
  if (!images || !images.length) {
    return `<div style="color: #999; padding: 1rem; text-align: center;">No ${label}</div>`;
  }
  return images
    .map(
      (image, i) => `
      <div class="preview-image-box" data-image="${image}">
        ${
          image
            ? `<img src="${image}" alt="${label} ${i + 1}">`
            : `${label} ${i + 1}`
        }
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

  // Basic fields from productForm
  setText("previewProductName", basicInfo.productName);
  setText("previewCategory", basicInfo.category);
  setText("previewSubCategory", basicInfo.subcategory);
  setText("previewSubItems", basicInfo.subitem);
  setText("previewPrice", basicInfo.price, (v) => (v ? `₱${v}` : "-"));
  setText("previewDiscountPercent", basicInfo.discountPercentage);
  setText("previewDiscountType", basicInfo.discountType);
  setText("previewVoucherType", basicInfo.voucherType);

  // Model Information (brand or model from basicInfo)
  setText("previewModelInfo", basicInfo.brand || basicInfo.model || "-");

  // Product Filters
  const filtersContainer = document.getElementById("previewProductFilters");
  if (filtersContainer) {
    if (basicInfo.filters && Object.keys(basicInfo.filters).length > 0) {
      const filterParts = Object.entries(basicInfo.filters)
        .map(([key, value]) => {
          const displayValue = Array.isArray(value) ? value.join(", ") : value;
          return `<div style="display: inline-block; background: #f0f0f0; padding: 4px 8px; border-radius: 4px; margin-right: 8px; margin-bottom: 4px; font-size: 0.9rem;">${key}: ${displayValue}</div>`;
        })
        .join("");
      filtersContainer.innerHTML = filterParts;
    } else {
      filtersContainer.textContent = "-";
    }
  }

  // Images (2 photos max from basic info)
  const imagesContainer = document.getElementById("previewImages");
  if (imagesContainer) {
    imagesContainer.innerHTML = generateImagePreviews(basicInfo.images || []);
    addImagePreviewHandlers();
  }

  // Description
  setText("previewDescription", description.description);
  setText("previewMaterials", description.materials);
  setText("previewDetailsFit", description.detailsFit);

  // Size Guide Photos
  const sizeGuideContainer = document.getElementById("previewSizeGuide");
  if (sizeGuideContainer) {
    sizeGuideContainer.innerHTML = generateGalleryPreviews(
      description.sizeGuide || [],
      "Size Guide Photo"
    );
    addImagePreviewHandlers();
  }

  // Certifications
  const certificationsContainer = document.getElementById(
    "previewCertifications"
  );
  if (certificationsContainer) {
    certificationsContainer.innerHTML = generateGalleryPreviews(
      description.certifications || [],
      "Certification"
    );
    addImagePreviewHandlers();
  }

  // Stock
  setText("previewTotalStock", stock.totalStock);

  const previewVariantsList = document.getElementById("previewVariantsList");
      stock.variants &&
      Array.isArray(stock.variants) &&
      stock.variants.length > 0
    ) {
      previewVariantsList.innerHTML = stock.variants
        .map(
          (v) => `
        <tr style="border-bottom: 1px solid #e5e7eb;">
          <td style="padding: 10px; border-right: 1px solid #e5e7eb;">${
            v.sku || "-"
          }</td>
          <td style="padding: 10px; border-right: 1px solid #e5e7eb;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span>${v.color || "-"}</span>
              ${
                v.colorHex
                  ? `<div style="width: 24px; height: 24px; background-color: ${v.colorHex}; border: 1px solid #ccc; border-radius: 4px;"></div>`
                  : ""
              }
            </div>
          </td>
          <td style="padding: 10px; border-right: 1px solid #e5e7eb;">${
            v.size || "-"
          }</td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb; font-weight: 600;">${
            v.stock ?? 0
          }</td>
          <td style="padding: 10px; text-align: center;">${v.lowStock ?? 0}</td>
        </tr>
      `
        )
        .join("");
    } else {
      previewVariantsList.innerHTML = `
        <tr>
          <td colspan="5" style="padding: 10px; text-align: center; color: #999;">No variants added</td>
        </tr>
      `;
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
