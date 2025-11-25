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
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 200px;">
        <div style="display:flex;flex-direction:column;gap:6px;">
          <button type="button" class="btn btn-secondary btn-select-sizes" data-row="${rowNumber}">Select Sizes</button>
          <div class="variant-size-summary" style="font-size:0.9rem;color:#374151"></div>
          <div class="variant-size-group" style="display:none"></div>
          <div class="size-stock-container" style="display:none;gap:6px;margin-top:6px;"></div>
        </div>
      </td>
      <td style="padding: 8px; border: 1px solid #e5e7eb; width: 140px;">
        <input type="number" min="0" placeholder="Low Stock" class="variant-input compact" name="lowStock_${rowNumber}" />
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

    // Setup photo upload preview for the new row
    const photoLabel = newRow.querySelector(".photo-upload-box");
    if (photoLabel) {
      setupVariantPhoto(photoLabel);
    }

    // wire size select -> enable/disable stock input
    const sizeSel = newRow.querySelector(`select[name="size_${rowNumber}"]`);
    // No single fallback stock column — stocks are per-size only.

    updateAddButtonState();
    console.log(`Added variant row ${rowNumber}`);
  }

  // Setup image preview behavior for a variant photo upload label
  function setupVariantPhoto(labelEl) {
    if (!labelEl) return;
    const input = labelEl.querySelector('input[type="file"]');
    const placeholder = labelEl.querySelector(".photo-upload-content");

    // clicking label should open file dialog
    labelEl.addEventListener("click", function (e) {
      // ignore clicks on a remove button if present
      if (
        e.target &&
        e.target.classList &&
        e.target.classList.contains("remove-photo")
      )
        return;
      if (input) input.click();
    });

    function setPreview(file) {
      // remove existing img if any
      const existing = labelEl.querySelector("img.upload-thumb");
      if (existing) existing.remove();

      if (file && file.type && file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = function (ev) {
          const img = document.createElement("img");
          img.className = "upload-thumb";
          img.src = ev.target.result;
          img.alt = "Variant photo";
          if (placeholder) placeholder.style.display = "none";
          labelEl.appendChild(img);
        };
        reader.readAsDataURL(file);
      } else {
        if (placeholder) placeholder.style.display = "";
      }
    }

    if (input) {
      input.addEventListener("change", function () {
        const file = input.files && input.files[0];
        if (file) setPreview(file);
        else setPreview(null);
      });
    }
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
    // Sum per-variant fallback stock inputs
    // Sum per-size stock inputs only
    const sizeStockInputs =
      variantTableBody.querySelectorAll(".size-stock-input");
    sizeStockInputs.forEach((input) => {
      const value = parseInt(input.value || "0", 10);
      if (!isNaN(value)) total += value;
    });

    const totalStockEl = document.getElementById("totalStock");
    if (totalStockEl) {
      totalStockEl.value = total;
    }

    return total;
  }

  // Expose updater globally so other scripts can call it after DOM changes
  window.updateTotalStock = updateTotalStock;

  // No single fallback stock inputs to wire — per-size stocks are handled elsewhere.

  // Attach photo preview handlers to existing photo upload boxes
  const existingPhotoLabels = document.querySelectorAll(".photo-upload-box");
  existingPhotoLabels.forEach((lbl) => setupVariantPhoto(lbl));

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

  // Initialize existing rows: wire up size-select/manage button/size inputs if present
  const existingRows = variantTableBody
    ? Array.from(variantTableBody.querySelectorAll("tr"))
    : [];
  existingRows.forEach((row) => {
    const sizeGroup = row.querySelector(".variant-size-group");
    const sizeContainer = row.querySelector(".size-stock-container");
    if (!sizeGroup) return;

    function buildSizeInputsForExistingRow() {
      if (!sizeContainer) return;
      const selected = Array.from(
        sizeGroup.querySelectorAll(".variant-size-checkbox")
      )
        .filter((cb) => cb.checked)
        .map((cb) => cb.dataset.size);
      sizeContainer.innerHTML = "";
      if (selected.length === 0) {
        sizeContainer.style.display = "none";
        return;
      }
      sizeContainer.style.display = "flex";
      selected.forEach((sz) => {
        const item = document.createElement("div");
        item.className = "size-stock-item";
        item.innerHTML = `<span style="font-weight:600">${sz}</span><input type="number" min="0" data-size="${sz}" class="size-stock-input" placeholder="0" style="width:80px;padding:6px;border-radius:6px;border:1px solid #e5e7eb;" />`;
        sizeContainer.appendChild(item);
        item
          .querySelector(".size-stock-input")
          .addEventListener("input", updateTotalStock);
      });
      updateTotalStock();
    }

    // wire up existing checkboxes
    const existingCbs = sizeGroup.querySelectorAll(".variant-size-checkbox");
    existingCbs.forEach((cb) =>
      cb.addEventListener("change", buildSizeInputsForExistingRow)
    );
    // initialize
    buildSizeInputsForExistingRow();
  });

  // Initial button state
  updateAddButtonState();

  console.log("Variant table management initialized");
});
