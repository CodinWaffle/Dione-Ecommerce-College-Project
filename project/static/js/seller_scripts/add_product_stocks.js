// Form submission and data persistence for add_product_stocks page
document.addEventListener("DOMContentLoaded", function () {
  console.log("add_product_stocks.js loaded");

  function storeProductStocks(formData) {
    try {
      localStorage.setItem("productStocksForm", JSON.stringify(formData));
      console.log("Stored productStocksForm:", formData);
    } catch (e) {
      console.error("Error storing product stocks:", e);
    }
  }

  function getVariantsData() {
    const variants = [];
    const rows = document.querySelectorAll("#variantTableBody tr");

    rows.forEach((row) => {
      const skuInput = row.querySelector('input[name^="sku_"]');
      const colorInput = row.querySelector('input[name^="color_"]');
      const colorPicker = row.querySelector('input[name^="color_picker_"]');
      const sizeSelect = row.querySelector('select[name^="size_"]');
      const stockInput = row.querySelector(".variant-stock-input");
      const lowStockInput = row.querySelector(
        'input[type="number"]:not(.variant-stock-input)'
      );

      const sku = skuInput?.value || "";
      const color = colorInput?.value || "";
      const colorHex = colorPicker?.value || "#000000";
      const size = sizeSelect?.value || "";
      // try to read a preview image src if user selected one
      const photoImg = row.querySelector(".photo-upload-box img.upload-thumb");
      const photo = photoImg ? photoImg.src || "" : "";
      // If stock input is disabled (no size selected), treat stock as 0
      let stock = 0;
      if (stockInput && !stockInput.disabled) {
        stock = parseInt(stockInput.value || "0", 10);
        if (isNaN(stock)) stock = 0;
      }
      const lowStock = parseInt(lowStockInput?.value || "0", 10);

      // Only include variant if there's identifying info or a selected size
      if (sku || color || size || stock > 0) {
        variants.push({
          sku: sku.trim(),
          color: color.trim(),
          colorHex: colorHex,
          photo: photo,
          size: size.trim(),
          stock: stock,
          lowStock: lowStock,
        });
      }
    });

    return variants;
  }

  // Form submit handler
  const form = document.getElementById("productStocksForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const variants = getVariantsData();
      let totalStock = 0;
      variants.forEach((v) => (totalStock += v.stock));

      const formData = {
        variants: variants,
        totalStock: totalStock,
        timestamp: Date.now(),
      };

      storeProductStocks(formData);

      // Store in products array for preview
      try {
        const existing = JSON.parse(localStorage.getItem("products") || "[]");
        existing.unshift({
          id: Date.now(),
          variants: variants,
          totalStock: totalStock,
        });
        localStorage.setItem("products", JSON.stringify(existing));
        console.log("Product saved to products array");
      } catch (e) {
        console.warn("Error saving to products array:", e);
      }

      // Navigate to preview
      window.location.href = "/seller/add_product_preview";
    });
  }

  // Back button handler
  const backBtn = document.getElementById("backBtn");
  if (backBtn) {
    backBtn.addEventListener("click", function () {
      window.location.href = "/seller/add_product_description";
    });
  }

  // Sync color picker with text input for existing first row
  // Only sync from text input to color picker, user can type color names
  const firstRow = document.querySelector("#variantTableBody tr");
  if (firstRow) {
    const colorInput = firstRow.querySelector('input[name^="color_"]');
    const colorPicker = firstRow.querySelector(
      '.color-picker, input[type="color"]'
    );

    if (colorInput && colorPicker) {
      colorInput.addEventListener("input", function () {
        const val = this.value.trim();
        if (val.startsWith("#") && (val.length === 4 || val.length === 7)) {
          colorPicker.value = val;
        }
      });
    }
  }

  console.log("Form handlers initialized");
});
