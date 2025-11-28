// Preview script: read stored form data and populate the preview DOM

function getFormData(key) {
  try {
    // Prefer localStorage (used by flow mirroring), but fall back to sessionStorage
    let raw = null;
    try {
      raw = localStorage.getItem(key);
    } catch (e) {
      raw = null;
    }
    if (!raw) {
      try {
        raw = sessionStorage.getItem(key);
      } catch (e) {
        raw = null;
      }
    }
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

function generateVariantRows(variants) {
  if (!variants || !Array.isArray(variants) || variants.length === 0) {
    return `<tr><td colspan="6" style="padding: 10px; text-align: center; color: #999;">No variants added</td></tr>`;
  }
  
  return variants.map((v) => {
    // Handle both old and new variant structures
    if (v.sizeStocks && Array.isArray(v.sizeStocks) && v.sizeStocks.length > 0) {
      // New structure: multiple sizes per variant
      return v.sizeStocks.map((sizeItem, index) => `
        <tr>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb;">
            ${index === 0 ? (
              v.photo
                ? `<div style="width:56px;height:56px;overflow:hidden;border-radius:6px;border:1px solid #e5e7eb"><img src="${v.photo}" style="width:100%;height:100%;object-fit:cover" alt="Variant"></div>`
                : `<div style="width:56px;height:56px;display:flex;align-items:center;justify-content:center;color:#999;background:#fafafa;border-radius:6px;border:1px dashed #e6e9ee">No</div>`
            ) : ''}
          </td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb; font-weight: 600;">
            ${index === 0 ? (v.sku || "-") : ""}
          </td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb;">
            ${index === 0 ? `
              <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background: ${v.colorHex || "#000"}; border: 1px solid #e5e7eb;"></div>
                <span style="font-weight: 600;">${v.color || "-"}</span>
              </div>
            ` : ""}
          </td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb; font-weight: 600;">
            ${sizeItem.size || "-"}
          </td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb; font-weight: 600;">
            ${sizeItem.stock ?? 0}
          </td>
          <td style="padding: 10px; text-align: center;">
            ${index === 0 ? (v.lowStock ?? 0) : ""}
          </td>
        </tr>
      `).join('');
    } else {
      // Old structure: single size per variant
      return `
        <tr>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb;">
            ${
              v.photo
                ? `<div style="width:56px;height:56px;overflow:hidden;border-radius:6px;border:1px solid #e5e7eb"><img src="${v.photo}" style="width:100%;height:100%;object-fit:cover" alt="Variant"></div>`
                : `<div style="width:56px;height:56px;display:flex;align-items:center;justify-content:center;color:#999;background:#fafafa;border-radius:6px;border:1px dashed #e6e9ee">No</div>`
            }
          </td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb; font-weight: 600;">${
            v.sku || "-"
          }</td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
              <div style="width: 20px; height: 20px; border-radius: 50%; background: ${
                v.colorHex || "#000"
              }; border: 1px solid #e5e7eb;"></div>
              <span style="font-weight: 600;">${v.color || "-"}</span>
            </div>
          </td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb; font-weight: 600;">${
            v.size || "-"
          }</td>
          <td style="padding: 10px; text-align: center; border-right: 1px solid #e5e7eb; font-weight: 600;">${
            v.stock ?? 0
          }</td>
          <td style="padding: 10px; text-align: center;">${v.lowStock ?? 0}</td>
        </tr>
      `;
    }
  }).join("");
}

function collectPreviewImages(basicInfo) {
  if (!basicInfo) return [];
  const output = [];
  const pushValue = (value) => {
    if (value && typeof value === "string") {
      output.push(value);
    }
  };
  pushValue(basicInfo.primaryImage);
  pushValue(basicInfo.secondaryImage);
  if (Array.isArray(basicInfo.images)) {
    basicInfo.images.forEach((img) => pushValue(img));
  } else if (typeof basicInfo.images === "string" && basicInfo.images.trim()) {
    try {
      const parsed = JSON.parse(basicInfo.images);
      if (Array.isArray(parsed)) {
        parsed.forEach((img) => pushValue(img));
      } else {
        pushValue(basicInfo.images);
      }
    } catch (err) {
      pushValue(basicInfo.images);
    }
  }
  return output;
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

  // Debug: Log the data we're working with
  console.log("Preview data:", { basicInfo, description, stock });
  console.log("Server preview flag:", window.__SERVER_PREVIEW);

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
    const imageList = collectPreviewImages(basicInfo);
    imagesContainer.innerHTML = generateImagePreviews(imageList);
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
  if (previewVariantsList) {
    if (
      stock.variants &&
      Array.isArray(stock.variants) &&
      stock.variants.length > 0
    ) {
      previewVariantsList.innerHTML = stock.variants
        .map(
          (v) => `
        <tr style="border-bottom: 1px solid #e5e7eb;">
          <td style="padding: 10px; border-right: 1px solid #e5e7eb; width: 72px; text-align: center;">
            ${
              v.photo
                ? `<div style="width:56px;height:56px;overflow:hidden;border-radius:6px;border:1px solid #e5e7eb"><img src="${v.photo}" style="width:100%;height:100%;object-fit:cover" alt="Variant"></div>`
                : `<div style="width:56px;height:56px;display:flex;align-items:center;justify-content:center;color:#999;background:#fafafa;border-radius:6px;border:1px dashed #e6e9ee">No</div>`
            }
          </td>
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
  document.addEventListener("DOMContentLoaded", function() {
    // Wait a bit for server data to be processed
    setTimeout(updatePreview, 100);
  });
} else {
  setTimeout(updatePreview, 100);
}

// Enhanced Add Product handler with authentication and error handling

// Enhanced error handling for authentication and server issues
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
    // Show loading state
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    
    // Attempt server-side save first (send JSON); if it fails, fall back to client-local flow
    (async function tryServerSave() {
      try {
        const basicInfo = safeParse("productForm") || {};
        const description = safeParse("productDescriptionForm") || {};
        const stock = safeParse("productStocksForm") || {};

        // Validate required fields before sending
        if (!basicInfo.productName || !basicInfo.category) {
          alert("Please fill in all required fields (Product Name and Category)");
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          return;
        }

        const payload = {
          step1: basicInfo,
          step2: description,
          step3: stock,
        };

        const res = await fetch(window.location.pathname, {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json, text/html",
          },
          body: JSON.stringify(payload),
        });

        // Check for authentication redirect
        if (res.url && res.url.includes('/login')) {
          alert("Your session has expired. Please log in again.");
          window.location.href = '/login';
          return;
        }

        if (res.ok) {
          // Success - redirect to products page
          const loc = res.url || "/seller/products";
          window.location.href = loc;
          return;
        } else {
          // Server error - show error message
          const errorText = await res.text();
          console.error("Server error:", res.status, errorText);
          alert("Error saving product. Please try again or contact support.");
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          return;
        }
      } catch (err) {
        console.warn("Server save failed, falling back to client-only save", err);
        
        // Check if it's a network error
        if (err.name === 'TypeError' && err.message.includes('fetch')) {
          alert("Network error. Please check your connection and try again.");
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          return;
        }
      }

      // Client-only localStorage flow (fallback)
      try {
        const basicInfo = safeParse("productForm") || {};
        const description = safeParse("productDescriptionForm") || {};
        const stock = safeParse("productStocksForm") || {};

        // Validate required fields
        if (!basicInfo.productName || !basicInfo.category) {
          alert("Please fill in all required fields (Product Name and Category)");
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          return;
        }

        // Build product object for the management list (keep full details inside object)
        const products = JSON.parse(localStorage.getItem("products") || "[]");
        const nextId =
          (products.reduce((m, p) => Math.max(m, Number(p.id || 0)), 0) || 0) + 1;

        const product = {
          id: nextId,
          name: basicInfo.productName || "Untitled Product",
          image: basicInfo.primaryImage || basicInfo.secondaryImage || "/static/image/banner.png",
          images: collectPreviewImages(basicInfo),
          price: Number(basicInfo.price) || 0,
          stock: Number(stock.totalStock) || (stock.variants ? stock.variants.reduce((s, v) => s + (Number(v.stock) || 0), 0) : 0),
          status: "active",
          category: basicInfo.category || "Uncategorized",
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

        // Show success message
        alert("Product saved locally. Note: This will only be visible in this browser.");
        
        // Redirect to product management page
        window.location.href = "/seller/products";
        
      } catch (localErr) {
        console.error("Local save also failed:", localErr);
        alert("Failed to save product. Please try again or contact support.");
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    })();
  });
})();
