// Enhanced Variant table management for add_product_stocks page
document.addEventListener("DOMContentLoaded", function () {
  console.log("Enhanced variant_table.js loaded");

  const addVariantBtn = document.getElementById("addVariantBtn");
  const variantTableBody = document.getElementById("variantTableBody");
  const MAX_VARIANTS = 10;

  let variantCounter = 1;

  // Photo upload is now handled by the new clean system in HTML template

  // Enhanced add variant row function
  function addVariantRow(rowNumber) {
    if (!variantTableBody) return;

    const newRow = document.createElement("tr");
    newRow.dataset.variant = rowNumber;
    newRow.innerHTML = `
      <td style="padding: 8px; border: 1px solid #e5e7eb; text-align: center; font-weight: 600; color: #6b7280; width: 36px;">
        ${rowNumber}
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; text-align: center; width: 60px;">
        <div class="variant-photo-upload" data-variant="${rowNumber}">
          <input type="file" accept="image/*" class="photo-input" style="display: none;">
          <div class="photo-placeholder">
            <i class="ri-camera-line"></i>
            <span>Add Photo</span>
          </div>
        </div>
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
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 200px;">
        <div style="display:flex;flex-direction:column;gap:6px;">
          <button type="button" class="btn btn-secondary btn-select-sizes" data-row="${rowNumber}" title="Select sizes and set stock levels">
            <i data-lucide="edit-3"></i>
            Select Sizes
          </button>
          <div class="variant-size-summary" style="font-size:0.9rem;color:#374151;min-height:20px;">
            <span class="no-sizes">No sizes selected</span>
          </div>
          <div class="variant-size-group" style="display:none"></div>
          <div class="size-stock-container" style="display:none;gap:6px;margin-top:6px;"></div>
        </div>
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 140px;">
        <input type="number" min="0" placeholder="Low Stock" class="variant-input compact" name="lowStock_${rowNumber}" />
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; text-align: center; width: 60px;">
        <div class="row-actions">
          <div class="row-total-stock">
            <span class="total-stock-badge zero">Total: 0</span>
          </div>
          <button type="button" class="delete-variant-btn" title="Remove variant">
            <i class="ri-close-line"></i>
          </button>
        </div>
      </td>
    `;

    variantTableBody.appendChild(newRow);

    // Photo upload will be handled by the new clean system

    // Setup delete button
    const deleteBtn = newRow.querySelector(".delete-variant-btn");
    if (deleteBtn) {
      deleteBtn.addEventListener("click", function () {
        newRow.remove();
        renumberRows();
        updateTotalStock();
        updateAddButtonState();
      });
    }

    // Setup color sync
    const colorInput = newRow.querySelector('input[name^="color_"]');
    const colorPicker = newRow.querySelector(".color-picker-input");
    syncColorPicker(colorInput, colorPicker);

    // Initialize Lucide icons
    if (window.lucide) {
      lucide.createIcons();
    }

    updateAddButtonState();
    console.log(`Added variant row ${rowNumber}`);
  }

  // Rest of the functions remain the same...
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

  function renumberRows() {
    const rows = variantTableBody.querySelectorAll("tr");
    rows.forEach((row, index) => {
      const numberCell = row.querySelector("td:first-child");
      if (numberCell) {
        numberCell.textContent = index + 1;
      }
      row.dataset.variant = index + 1;
    });
  }

  function syncColorPicker(colorInput, colorPicker) {
    if (!colorInput || !colorPicker) return;

    colorInput.addEventListener("input", function () {
      const val = this.value.trim();
      if (val.startsWith("#") && (val.length === 4 || val.length === 7)) {
        colorPicker.value = val;
      }
    });

    colorPicker.addEventListener("input", function () {
      const hexValue = this.value;
      if (!colorInput.value.trim() || colorInput.value.trim().startsWith("#")) {
        colorInput.value = hexValue;
      }
    });
  }

  function updateTotalStock() {
    if (!variantTableBody) return;

    let total = 0;
    const sizeStockInputs = variantTableBody.querySelectorAll(".size-stock-input");
    sizeStockInputs.forEach((input) => {
      const value = parseInt(input.value || "0", 10);
      if (!isNaN(value)) total += value;
    });

    const totalStockEl = document.getElementById("totalStockDisplay");
    if (totalStockEl) {
      totalStockEl.textContent = total;
    }

    return total;
  }

  // Event listeners
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

  // Global functions
  window.updateTotalStock = updateTotalStock;

  // Photo upload is now handled by the new clean system in HTML template
  // This file focuses only on variant table management

  // Initialize
  updateAddButtonState();

  console.log("Enhanced variant table management initialized");
});