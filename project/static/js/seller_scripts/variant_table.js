// Variant table management for add_product_stocks page
document.addEventListener("DOMContentLoaded", function () {
  console.log("variant_table.js loaded");

  const addVariantBtn = document.getElementById("addVariantBtn");
  const variantTableBody = document.getElementById("variantTableBody");
  const MAX_VARIANTS = 10;

  let variantCounter = 1; // Start from 1 as we already have one row

  function updateAddButtonState() {
    const currentRows = variantTableBody.querySelectorAll("tr").length;
    if (addVariantBtn) {
      if (currentRows >= MAX_VARIANTS) {
        addVariantBtn.disabled = true;
        addVariantBtn.style.opacity = "0.5";
        addVariantBtn.style.cursor = "not-allowed";
      } else {
        addVariantBtn.disabled = false;
        addVariantBtn.style.opacity = "1";
        addVariantBtn.style.cursor = "pointer";
      }
    }
  }

  if (addVariantBtn) {
    addVariantBtn.addEventListener("click", function (e) {
      e.preventDefault();
      const currentRows = variantTableBody.querySelectorAll("tr").length;
      if (currentRows >= MAX_VARIANTS) {
        alert(`Maximum ${MAX_VARIANTS} variants allowed`);
        return;
      }
      variantCounter++;
      addVariantRow(variantCounter);
    });
  }

  function addVariantRow(rowNumber) {
    if (!variantTableBody) return;

    const newRow = document.createElement("tr");
    newRow.innerHTML = `
      <td style="padding: 8px; border: 1px solid #e5e7eb; text-align: center; font-weight: 600; color: #6b7280; width: 36px;">
        ${rowNumber}
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; text-align: center; width: 60px;">
        <label class="photo-upload-box grey" style="margin: 0 auto">
          <input type="file" style="display: none" />
          <div class="photo-upload-content">
            <i class="ri-image-add-line" style="font-size: 1.2rem; color: #a259f7"></i>
          </div>
        </label>
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 180px;">
        <input type="text" name="sku_${rowNumber}" placeholder="SKU" class="variant-input compact" />
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 140px;">
        <div style="display: flex; align-items: center; gap: 6px;">
          <input type="text" name="color_${rowNumber}" placeholder="Color" class="variant-input compact" style="flex: 1;" />
          <input type="color" name="color_picker_${rowNumber}" class="color-picker-input" value="#000000" style="width: 32px; height: 32px; border: 1px solid #e5e7eb; border-radius: 4px; cursor: pointer; padding: 2px;" />
        </div>
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 140px;">
        <select name="size_${rowNumber}" class="variant-input compact">
          <option value="">Select</option>
          <option value="XS">XS</option>
          <option value="S">S</option>
          <option value="M">M</option>
          <option value="L">L</option>
          <option value="XL">XL</option>
        </select>
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 140px;">
        <input type="number" min="0" placeholder="Stock" class="variant-input compact variant-stock-input" />
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 140px;">
        <input type="number" min="0" placeholder="Low Stock" class="variant-input compact" />
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; text-align: center; width: 60px;">
        <button type="button" class="delete-variant-btn" title="Remove variant">
          <i class="ri-close-line"></i>
        </button>
      </td>
    `;

    variantTableBody.appendChild(newRow);

    // Add delete button listener
    const deleteBtn = newRow.querySelector(".delete-variant-btn");
    if (deleteBtn) {
      deleteBtn.addEventListener("click", function () {
        newRow.remove();
        renumberRows();
        updateTotalStock();
        updateAddButtonState();
      });
    }

    // Sync color picker with text input for the new row
    const colorInput = newRow.querySelector('input[name^="color_"]');
    const colorPicker = newRow.querySelector(".color-picker-input");
    syncColorPicker(colorInput, colorPicker);

    // Add event listener for the new stock input to update total
    const stockInput = newRow.querySelector(".variant-stock-input");
    if (stockInput) {
      stockInput.addEventListener("input", updateTotalStock);
    }

    updateAddButtonState();
    console.log(`Added variant row ${rowNumber}`);
  }

  function renumberRows() {
    const rows = variantTableBody.querySelectorAll("tr");
    rows.forEach((row, index) => {
      const numberCell = row.querySelector("td:first-child");
      if (numberCell) {
        numberCell.textContent = index + 1;
      }
    });
  }

  function syncColorPicker(colorInput, colorPicker) {
    if (!colorInput || !colorPicker) return;

    // Only sync from text input to color picker, not the reverse
    // User types color name or hex code, picker updates if valid hex
    colorInput.addEventListener("input", function () {
      const val = this.value.trim();
      if (val.startsWith("#") && (val.length === 4 || val.length === 7)) {
        colorPicker.value = val;
      }
    });
  }

  function updateTotalStock() {
    if (!variantTableBody) return;

    let total = 0;
    const stockInputs = variantTableBody.querySelectorAll(
      ".variant-stock-input"
    );
    stockInputs.forEach((input) => {
      const value = parseInt(input.value || "0", 10);
      if (!isNaN(value)) {
        total += value;
      }
    });

    const totalStockEl = document.getElementById("totalStock");
    if (totalStockEl) {
      totalStockEl.value = total;
    }

    return total;
  }

  // Attach input listeners to existing stock inputs
  const existingStockInputs = document.querySelectorAll(".variant-stock-input");
  existingStockInputs.forEach((input) => {
    input.addEventListener("input", updateTotalStock);
  });

  // Attach delete button listeners to existing rows (except first row)
  const existingDeleteBtns = document.querySelectorAll(".delete-variant-btn");
  existingDeleteBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const row = btn.closest("tr");
      if (row) {
        row.remove();
        renumberRows();
        updateTotalStock();
        updateAddButtonState();
      }
    });
  });

  // Initial button state
  updateAddButtonState();

  console.log("Variant table management initialized");
});
