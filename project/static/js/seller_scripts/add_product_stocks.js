// Form submission and data persistence for add_product_stocks page
document.addEventListener("DOMContentLoaded", function () {
  console.log("add_product_stocks.js loaded");

  // Debug: Check if photo boxes exist
  setTimeout(() => {
    const photoBoxes = document.querySelectorAll(".photo-upload-box");
    console.log(
      "Photo boxes found in add_product_stocks.js:",
      photoBoxes.length
    );
    photoBoxes.forEach((box, index) => {
      console.log(`Photo box ${index + 1}:`, box);
      const input = box.querySelector('input[type="file"]');
      console.log(`  - Has file input: ${!!input}`);
      console.log(`  - Setup status: ${box.dataset.photoSetup || "not set"}`);
    });
  }, 1000);

  // Grouped sizes available for selection. Each group has a name and sizes.
  const AVAILABLE_SIZE_GROUPS = [
    {
      name: "Clothing",
      hint: "Shirts, tops, dresses",
      sizes: ["XS", "S", "M", "L", "XL", "XXL", "One size", "Free size"],
    },
    {
      name: "Shoes",
      hint: "US / EU shoe sizes",
      sizes: [
        "US 5",
        "US 6",
        "US 7",
        "US 8",
        "US 9",
        "US 10",
        "US 11",
        "EU 36",
        "EU 37",
        "EU 38",
        "EU 39",
        "EU 40",
      ],
    },
    {
      name: "Rings",
      hint: "Ring sizes",
      sizes: [
        "Ring 4",
        "Ring 5",
        "Ring 6",
        "Ring 7",
        "Ring 8",
        "Ring 9",
        "Ring 10",
      ],
    },
    {
      name: "Misc",
      hint: "Waist, custom sizes",
      sizes: ["Waist 28", "Waist 30", "Waist 32", "Other"],
    },
  ];

  // Modal elements
  const sizeModal = document.getElementById("sizeSelectModal");
  const sizeOptionsContainer = document.getElementById("sizeOptionsContainer");
  const sizeModalSave = document.getElementById("sizeModalSave");
  const sizeModalCancel = document.getElementById("sizeModalCancel");
  const sizeModalClose = document.getElementById("sizeModalClose");

  // Initialize total stock display on page load
  setTimeout(() => {
    if (typeof window.updateTotalStock === "function") {
      window.updateTotalStock();
    }
  }, 100);

  let currentSizeModalRow = null; // reference to <tr> for which modal is opened

  function addCustomSizeToList(sizeName, stockValue, container) {
    const customItem = document.createElement("div");
    customItem.className = "custom-size-item";
    customItem.dataset.size = sizeName;

    const nameSpan = document.createElement("span");
    nameSpan.className = "custom-size-name";
    nameSpan.textContent = sizeName;

    const stockInput = document.createElement("input");
    stockInput.type = "number";
    stockInput.className = "stock-input-small";
    stockInput.value = stockValue;
    stockInput.min = "0";
    stockInput.dataset.size = sizeName;

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "remove-custom-size";
    removeBtn.innerHTML = '<i data-lucide="x"></i>';
    removeBtn.title = "Remove custom size";

    removeBtn.addEventListener("click", () => {
      customItem.remove();
    });

    customItem.appendChild(nameSpan);
    customItem.appendChild(stockInput);
    customItem.appendChild(removeBtn);
    container.appendChild(customItem);

    // Initialize Lucide icons for the new button
    if (window.lucide) {
      lucide.createIcons();
    }
  }

  function openSizeModalForRow(row) {
    if (!sizeModal || !sizeOptionsContainer) return;
    currentSizeModalRow = row;
    sizeOptionsContainer.innerHTML = "";

    // read existing size stocks from the row if any
    const existingSizeInputs = row.querySelectorAll(".size-stock-input");
    const existingMap = {};
    existingSizeInputs.forEach((inp) => {
      const s = inp.dataset.size;
      existingMap[s] = inp.value || "0";
    });

    // Render groups with headers for clarity (e.g., Clothing, Shoes, Rings)
    AVAILABLE_SIZE_GROUPS.forEach((group) => {
      const groupWrap = document.createElement("div");
      groupWrap.className = "size-group-container";

      const header = document.createElement("div");
      header.className = "size-group-header";
      const title = document.createElement("strong");
      title.textContent = group.name;
      const hint = document.createElement("span");
      hint.className = "size-group-hint";
      hint.textContent = ` ${group.hint ? "— " + group.hint : ""}`;
      header.appendChild(title);
      header.appendChild(hint);

      const grid = document.createElement("div");
      grid.className = "size-group-grid";

      group.sizes.forEach((sz) => {
        const wrapper = document.createElement("div");
        wrapper.className = "size-selection-box";
        wrapper.dataset.size = sz;

        if (existingMap[sz] !== undefined) {
          wrapper.classList.add("selected");
        }

        const sizeName = document.createElement("div");
        sizeName.className = "size-name";
        sizeName.textContent = sz;

        const badge = document.createElement("div");
        badge.className = "size-category-badge";
        badge.textContent = group.name;

        const stockInput = document.createElement("input");
        stockInput.type = "number";
        stockInput.min = "0";
        stockInput.placeholder = "0";
        stockInput.className = "stock-input-small";
        stockInput.dataset.size = sz;
        stockInput.value = existingMap[sz] || "";

        if (!existingMap[sz] || existingMap[sz] === undefined) {
          stockInput.style.display = "none";
        }

        // Handle box click to select/deselect
        wrapper.addEventListener("click", (e) => {
          if (e.target === stockInput) return; // Don't toggle when clicking input

          wrapper.classList.toggle("selected");
          if (wrapper.classList.contains("selected")) {
            stockInput.style.display = "block";
            if (!stockInput.value) {
              stockInput.value = "0";
            }
            setTimeout(() => stockInput.focus(), 50);
          } else {
            stockInput.style.display = "none";
            stockInput.value = "";
          }
        });

        // Handle stock input changes
        stockInput.addEventListener("input", (e) => {
          const value = parseInt(e.target.value) || 0;
          if (value < 0) {
            e.target.value = "0";
          }
        });

        wrapper.appendChild(sizeName);
        wrapper.appendChild(badge);
        wrapper.appendChild(stockInput);
        grid.appendChild(wrapper);
      });

      // If the group doesn't already include an 'Other' control, add one so
      // users can type custom sizes for this specific group (allows multiple)
      if (!group.sizes.includes("Other")) {
        const sz = "Other";
        const wrapper = document.createElement("div");
        wrapper.className = "size-options-row size-options-other";

        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.className = "modal-size-checkbox";
        cb.dataset.size = sz;
        cb.id = `modal_size_${group.name.replace(/\s+/g, "_")}_Other`;

        const lbl = document.createElement("label");
        lbl.htmlFor = cb.id;
        lbl.className = "size-label-with-badge";
        lbl.textContent = sz;

        const badge = document.createElement("span");
        badge.className = "size-category-badge";
        badge.textContent = group.name;
        lbl.appendChild(badge);

        const customInp = document.createElement("input");
        customInp.type = "text";
        customInp.placeholder = "Type sizes, comma separated (e.g. 7 UK, 28W)";
        customInp.className = "modal-size-custom";
        customInp.dataset.for = cb.id;

        const stockInp = document.createElement("input");
        stockInp.type = "number";
        stockInp.min = "0";
        stockInp.placeholder = "0";
        stockInp.className = "modal-size-stock";
        stockInp.dataset.for = cb.id;

        cb.addEventListener("change", () => {
          customInp.disabled = !cb.checked;
          stockInp.disabled = !cb.checked;
          wrapper.classList.toggle("size-selected", cb.checked);
          if (!cb.checked) {
            customInp.value = "";
            stockInp.value = "";
          }
        });
        customInp.disabled = true;
        stockInp.disabled = true;

        wrapper.appendChild(cb);
        wrapper.appendChild(lbl);
        wrapper.appendChild(customInp);
        wrapper.appendChild(stockInp);
        grid.appendChild(wrapper);
      }

      groupWrap.appendChild(header);
      groupWrap.appendChild(grid);
      sizeOptionsContainer.appendChild(groupWrap);
    });

    // Add custom size section
    // Preview section removed for more compact modal design

    const customSizeSection = document.createElement("div");
    customSizeSection.className = "custom-size-section";

    const customHeader = document.createElement("div");
    customHeader.className = "custom-size-header";

    const customIcon = document.createElement("div");
    customIcon.className = "custom-size-icon";
    customIcon.innerHTML = '<i data-lucide="plus"></i>';

    const customTitle = document.createElement("h4");
    customTitle.textContent = "Add Custom Sizes";

    customHeader.appendChild(customIcon);
    customHeader.appendChild(customTitle);

    const inputGroup = document.createElement("div");
    inputGroup.className = "custom-size-input-group";

    const inputWrapper = document.createElement("div");
    inputWrapper.className = "custom-size-input-wrapper";

    const inputLabel = document.createElement("label");
    inputLabel.textContent = "Custom Size Name";

    const customInput = document.createElement("input");
    customInput.type = "text";
    customInput.className = "custom-size-input";
    customInput.placeholder = "e.g., 7 UK, 28W, Medium-Large";
    customInput.id = "customSizeInput";

    const stockWrapper = document.createElement("div");
    stockWrapper.className = "custom-size-input-wrapper";

    const stockLabel = document.createElement("label");
    stockLabel.textContent = "Stock Quantity";

    const customStockInput = document.createElement("input");
    customStockInput.type = "number";
    customStockInput.className = "custom-size-input";
    customStockInput.placeholder = "0";
    customStockInput.min = "0";
    customStockInput.id = "customStockInput";

    const addBtn = document.createElement("button");
    addBtn.type = "button";
    addBtn.className = "add-custom-size-btn";
    addBtn.innerHTML = '<i data-lucide="plus"></i>Add Size';

    inputWrapper.appendChild(inputLabel);
    inputWrapper.appendChild(customInput);
    stockWrapper.appendChild(stockLabel);
    stockWrapper.appendChild(customStockInput);

    inputGroup.appendChild(inputWrapper);
    inputGroup.appendChild(stockWrapper);
    inputGroup.appendChild(addBtn);

    const customSizesList = document.createElement("div");
    customSizesList.className = "custom-sizes-list";
    customSizesList.id = "customSizesList";

    // Load existing custom sizes
    const existingCustomSizes = Object.keys(existingMap).filter((size) => {
      return !AVAILABLE_SIZE_GROUPS.some((group) => group.sizes.includes(size));
    });

    existingCustomSizes.forEach((customSize) => {
      addCustomSizeToList(customSize, existingMap[customSize], customSizesList);
    });

    // Add custom size functionality
    addBtn.addEventListener("click", () => {
      const sizeName = customInput.value.trim();
      const stockValue = customStockInput.value || "0";

      if (sizeName) {
        addCustomSizeToList(sizeName, stockValue, customSizesList);
        customInput.value = "";
        customStockInput.value = "";
      }
    });

    // Allow Enter key to add custom size
    customInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        addBtn.click();
      }
    });

    customSizeSection.appendChild(customHeader);
    customSizeSection.appendChild(inputGroup);
    customSizeSection.appendChild(customSizesList);
    sizeOptionsContainer.appendChild(customSizeSection);

    // Initialize Lucide icons
    if (window.lucide) {
      lucide.createIcons();
    }

    // Preview functionality removed for more compact modal design

    // If existing saved sizes contain keys that are not part of any group,
    // prefill the 'Other' custom input with the first such key.
    try {
      // build flat set of known sizes
      const knownSizes = new Set();
      AVAILABLE_SIZE_GROUPS.forEach((g) =>
        g.sizes.forEach((s) => knownSizes.add(s))
      );
      const customKeys = Object.keys(existingMap).filter(
        (k) => !knownSizes.has(k)
      );
      if (customKeys.length) {
        // Append each saved custom size as its own selectable row inside the
        // Misc group (last group). This makes it easy for the seller to edit
        // previously-entered custom sizes individually.
        const allGroups = Array.from(
          sizeOptionsContainer.querySelectorAll(".size-group-container")
        );
        const miscGroup = allGroups[allGroups.length - 1];
        const miscGrid = miscGroup
          ? miscGroup.querySelector(".size-group-grid")
          : null;
        let customIndex = 0;
        customKeys.forEach((ck) => {
          const wrapper = document.createElement("div");
          wrapper.className = "size-options-row";

          const cb = document.createElement("input");
          cb.type = "checkbox";
          cb.className = "modal-size-checkbox";
          cb.dataset.size = ck;
          cb.id = `modal_size_custom_${customIndex++}`;
          cb.checked = true;

          const lbl = document.createElement("label");
          lbl.htmlFor = cb.id;
          lbl.className = "size-label-with-badge";
          lbl.textContent = ck;

          const badge = document.createElement("span");
          badge.className = "size-category-badge";
          badge.textContent = "Custom";
          lbl.appendChild(badge);

          const stockInput = document.createElement("input");
          stockInput.type = "number";
          stockInput.min = "0";
          stockInput.className = "modal-size-stock";
          stockInput.dataset.for = cb.id;
          stockInput.value = existingMap[ck] || "";

          wrapper.appendChild(cb);
          wrapper.appendChild(lbl);
          wrapper.appendChild(stockInput);
          if (miscGrid) miscGrid.appendChild(wrapper);
          // show selected state for prefills
          if (cb.checked) wrapper.classList.add("size-selected");
        });
      }
    } catch (e) {
      // ignore prefill errors
    }

    // Show modal via CSS class for consistent styling
    try {
      sizeModal.classList.add("active");
    } catch (e) {
      sizeModal.style.display = "block";
    }
  }

  function closeSizeModal() {
    if (!sizeModal) return;
    try {
      sizeModal.classList.remove("active");
    } catch (e) {
      sizeModal.style.display = "none";
    }
    currentSizeModalRow = null;
  }

  function saveSizeModal() {
    if (!currentSizeModalRow) return;

    // Get selected size boxes
    const selectedBoxes = Array.from(
      sizeOptionsContainer.querySelectorAll(".size-selection-box.selected")
    );

    // Get custom sizes
    const customSizes = Array.from(
      sizeOptionsContainer.querySelectorAll(".custom-size-item")
    );

    const sizeGroup = currentSizeModalRow.querySelector(".variant-size-group");
    const sizeSummary = currentSizeModalRow.querySelector(
      ".variant-size-summary"
    );

    // Remove existing size-stock-inputs in the row
    const existing = Array.from(
      currentSizeModalRow.querySelectorAll(".size-stock-input")
    );
    existing.forEach((e) => e.remove());

    // Ensure variant-size-group exists
    if (sizeGroup) sizeGroup.innerHTML = "";

    const stocks = [];
    // Prepare visible size-stock container
    const sizeContainer = currentSizeModalRow.querySelector(
      ".size-stock-container"
    );
    if (sizeContainer) sizeContainer.innerHTML = "";

    // Process selected size boxes
    selectedBoxes.forEach((box) => {
      const sizeName = box.dataset.size;
      const stockInput = box.querySelector(".stock-input-small");
      const stockValue = parseInt(stockInput?.value || "0", 10) || 0;

      stocks.push({ size: sizeName, stock: stockValue });
      addSizeToRow(sizeName, stockValue, sizeGroup, sizeContainer);
    });

    // Process custom sizes
    customSizes.forEach((customItem) => {
      const sizeName = customItem.dataset.size;
      const stockInput = customItem.querySelector(".stock-input-small");
      const stockValue = parseInt(stockInput?.value || "0", 10) || 0;

      stocks.push({ size: sizeName, stock: stockValue });
      addSizeToRow(sizeName, stockValue, sizeGroup, sizeContainer);
    });

    // Update visible summary with enhanced formatting
    if (sizeSummary) {
      if (stocks.length === 0) {
        sizeSummary.innerHTML =
          '<span class="no-sizes">No sizes selected</span>';
      } else {
        // Sort sizes logically (XS, S, M, L, XL, etc.)
        const sortedStocks = sortSizesLogically(stocks);
        const totalVariantStock = sortedStocks.reduce(
          (sum, s) => sum + s.stock,
          0
        );

        const summaryHtml = sortedStocks
          .map((s) => {
            const stockClass =
              s.stock === 0
                ? "out-of-stock"
                : s.stock < 5
                ? "low-stock"
                : "in-stock";
            return `<span class="size-summary-item ${stockClass}">${s.size}: ${s.stock}</span>`;
          })
          .join(" • ");

        sizeSummary.innerHTML = `
          <div class="size-summary-header">
            <strong>${stocks.length} size${
          stocks.length > 1 ? "s" : ""
        } selected (Total: ${totalVariantStock})</strong>
          </div>
          <div class="size-summary-details">${summaryHtml}</div>
        `;
      }
    }

    // Update row total stock display
    updateRowTotalStock(currentSizeModalRow, stocks);

    // Trigger total update
    if (typeof window.updateTotalStock === "function") {
      window.updateTotalStock();
    }

    // Show success feedback
    showSaveSuccessFeedback(currentSizeModalRow);

    closeSizeModal();
  }

  function addSizeToRow(sizeName, stockValue, sizeGroup, sizeContainer) {
    if (sizeGroup) {
      const hiddenCb = document.createElement("input");
      hiddenCb.type = "checkbox";
      hiddenCb.className = "variant-size-checkbox";
      hiddenCb.dataset.size = sizeName;
      hiddenCb.checked = true;
      hiddenCb.style.display = "none";
      sizeGroup.appendChild(hiddenCb);
    }

    if (sizeContainer) {
      const item = document.createElement("div");
      item.className = "size-stock-item";
      item.style.display = "flex";
      item.style.alignItems = "center";
      item.style.gap = "8px";
      item.style.marginBottom = "6px";

      const label = document.createElement("span");
      label.textContent = sizeName;
      label.style.fontWeight = "600";
      label.style.width = "60px";

      const inp = document.createElement("input");
      inp.type = "number";
      inp.min = "0";
      inp.className = "size-stock-input";
      inp.dataset.size = sizeName;
      inp.value = stockValue;
      inp.style.width = "120px";
      inp.style.padding = "6px";
      inp.style.border = "1px solid #e5e7eb";
      inp.style.borderRadius = "6px";

      inp.addEventListener("input", () => {
        if (typeof window.updateTotalStock === "function")
          window.updateTotalStock();
      });

      item.appendChild(label);
      item.appendChild(inp);
      sizeContainer.appendChild(item);
    }
  }

  // Modal event listeners
  if (sizeModalSave) sizeModalSave.addEventListener("click", saveSizeModal);
  if (sizeModalCancel)
    sizeModalCancel.addEventListener("click", closeSizeModal);
  if (sizeModalClose) sizeModalClose.addEventListener("click", closeSizeModal);

  // Close modal when clicking outside content (overlay)
  if (sizeModal) {
    sizeModal.addEventListener("click", (e) => {
      if (e.target === sizeModal) closeSizeModal();
    });
  }

  // Delegate click for Select Sizes buttons (existing and future rows)
  document.addEventListener("click", function (e) {
    const btn = e.target.closest && e.target.closest(".btn-select-sizes");
    if (!btn) return;
    const row = btn.closest("tr");
    if (!row) return;
    openSizeModalForRow(row);
  });

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
      // size: prefer a single select (legacy/original design), fallback to checkbox group
      const sizeGroup = row.querySelector(".variant-size-group");
      const lowStockInput = row.querySelector('input[name^="lowStock_"]');

      const sku = skuInput?.value || "";
      const color = colorInput?.value || "";
      const colorHex = colorPicker?.value || "#000000";
      // collect size and per-size stocks if present
      let size = "";
      const sizeStocks = [];
      if (sizeGroup) {
        const checked = Array.from(
          sizeGroup.querySelectorAll(".variant-size-checkbox")
        )
          .filter((cb) => cb.checked)
          .map((cb) => cb.dataset.size);
        size = checked.join(",");
        checked.forEach((s) => {
          const inputs = row.querySelectorAll(".size-stock-input");
          const inp = Array.from(inputs).find((i) => i.dataset.size === s);
          const val = inp ? parseInt(inp.value || "0", 10) : 0;
          sizeStocks.push({ size: s, stock: isNaN(val) ? 0 : val });
        });
      }
      // try to read a preview image src if user selected one
      const photoImg = row.querySelector(".photo-upload-box img.upload-thumb");
      const photo = photoImg ? photoImg.src || "" : "";
      // Derive total stock from per-size stocks only (no single-stock column)
      let stock = 0;
      if (sizeStocks.length) {
        sizeStocks.forEach((ss) => (stock += ss.stock || 0));
      } else {
        stock = 0;
      }
      const lowStock = parseInt(lowStockInput?.value || "0", 10);

      // Only include variant if there's identifying info or a selected size
      if (sku || color || size || stock > 0) {
        const v = {
          sku: sku.trim(),
          color: color.trim(),
          colorHex: colorHex,
          photo: photo,
          size: size.trim(),
          stock: stock,
          lowStock: lowStock,
        };
        if (sizeStocks.length) v.sizeStocks = sizeStocks;
        variants.push(v);
      }
    });

    return variants;
  }

  // Enhanced Form submit handler with proper navigation
  const form = document.getElementById("productStocksForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      handleFormSubmission();
    });
  }

  // Handle form submission with AJAX and navigation
  async function handleFormSubmission() {
    const submitBtn = document.querySelector('.btn-save');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="ri-loader-4-line" style="animation: spin 1s linear infinite;"></i> Saving...';
    
    try {
      // Get all form data
      const variants = getVariantsData();
      let totalStock = 0;
      variants.forEach((v) => (totalStock += v.stock));

      // Get previous step data from session storage or localStorage
      const step1Data = getStoredData('productForm') || getStoredData('step1') || {};
      const step2Data = getStoredData('productDescriptionForm') || getStoredData('step2') || {};
      
      const payload = {
        step1: step1Data,
        step2: step2Data,
        step3: {
          variants: variants,
          totalStock: totalStock,
          timestamp: Date.now(),
        }
      };

      console.log('Submitting payload:', payload);

      // Submit to server
      const response = await fetch(window.location.pathname, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const result = await response.json();
        
        if (result.success) {
          // Clear stored form data
          clearStoredFormData();
          
          // Navigate to preview
          window.location.href = result.next;
        } else {
          throw new Error(result.error || 'Server returned error');
        }
      } else {
        throw new Error(`Server error: ${response.status}`);
      }
      
    } catch (error) {
      console.error('Form submission error:', error);
      alert('Error saving product: ' + error.message);
      
      // Restore button
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  }

  // Helper function to get stored data from various sources
  function getStoredData(key) {
    try {
      // Try localStorage first
      let data = localStorage.getItem(key);
      if (data) return JSON.parse(data);
      
      // Try sessionStorage
      data = sessionStorage.getItem(key);
      if (data) return JSON.parse(data);
      
      return null;
    } catch (e) {
      console.warn(`Failed to get stored data for ${key}:`, e);
      return null;
    }
  }

  // Helper function to clear stored form data
  function clearStoredFormData() {
    try {
      localStorage.removeItem('productForm');
      localStorage.removeItem('productDescriptionForm');
      localStorage.removeItem('productStocksForm');
      sessionStorage.removeItem('productForm');
      sessionStorage.removeItem('productDescriptionForm');
      sessionStorage.removeItem('productStocksForm');
      sessionStorage.removeItem('step1');
      sessionStorage.removeItem('step2');
      sessionStorage.removeItem('step3');
    } catch (e) {
      console.warn('Failed to clear stored form data:', e);
    }
  }

  // Back button handler
  const backBtn = document.getElementById("backBtn");
  if (backBtn) {
    backBtn.addEventListener("click", function () {
      window.location.href = "/seller/add_product_description";
    });
  }

  // Sync color picker with text input for all rows (bidirectional)
  function setupColorSync() {
    const rows = document.querySelectorAll("#variantTableBody tr");

    rows.forEach((row) => {
      const colorInput = row.querySelector('input[name^="color_"]');
      const colorPicker = row.querySelector(
        '.color-picker, input[type="color"]'
      );

      if (colorInput && colorPicker) {
        // Sync from text input to color picker (when user types hex)
        colorInput.addEventListener("input", function () {
          const val = this.value.trim();
          if (val.startsWith("#") && (val.length === 4 || val.length === 7)) {
            colorPicker.value = val;
          }
        });

        // Sync from color picker to text input (when user picks color)
        colorPicker.addEventListener("input", function () {
          const hexValue = this.value;
          // Only update if the text input is empty or already contains a hex value
          if (
            !colorInput.value.trim() ||
            colorInput.value.trim().startsWith("#")
          ) {
            colorInput.value = hexValue;
          }
        });

        // Also sync on change event for better compatibility
        colorPicker.addEventListener("change", function () {
          const hexValue = this.value;
          if (
            !colorInput.value.trim() ||
            colorInput.value.trim().startsWith("#")
          ) {
            colorInput.value = hexValue;
          }
        });
      }
    });
  }

  // Initial setup
  setupColorSync();

  // Re-setup when new rows are added (if there's dynamic row addition)
  const addVariantBtn = document.getElementById("addVariantBtn");
  if (addVariantBtn) {
    addVariantBtn.addEventListener("click", function () {
      // Small delay to allow DOM to update
      setTimeout(setupColorSync, 100);
    });
  }

  console.log("Form handlers initialized");

  // Helper function to sort sizes logically
  function sortSizesLogically(stocks) {
    const sizeOrder = {
      XS: 1,
      S: 2,
      M: 3,
      L: 4,
      XL: 5,
      XXL: 6,
      "One size": 7,
      "Free size": 8,
      "US 5": 10,
      "US 6": 11,
      "US 7": 12,
      "US 8": 13,
      "US 9": 14,
      "US 10": 15,
      "US 11": 16,
      "EU 36": 20,
      "EU 37": 21,
      "EU 38": 22,
      "EU 39": 23,
      "EU 40": 24,
      "EU 41": 25,
      "EU 42": 26,
      "Ring 4": 30,
      "Ring 5": 31,
      "Ring 6": 32,
      "Ring 7": 33,
      "Ring 8": 34,
      "Ring 9": 35,
      "Ring 10": 36,
      "Waist 28": 40,
      "Waist 30": 41,
      "Waist 32": 42,
    };

    return stocks.sort((a, b) => {
      const orderA = sizeOrder[a.size] || 999;
      const orderB = sizeOrder[b.size] || 999;
      if (orderA !== orderB) return orderA - orderB;
      return a.size.localeCompare(b.size);
    });
  }

  // Update row total stock display
  function updateRowTotalStock(row, stocks) {
    const totalStock = stocks.reduce((sum, s) => sum + s.stock, 0);
    let totalStockEl = row.querySelector(".row-total-stock");

    if (!totalStockEl) {
      // Create total stock display if it doesn't exist
      const actionsCell = row.querySelector("td:last-child");
      if (actionsCell) {
        totalStockEl = document.createElement("div");
        totalStockEl.className = "row-total-stock";
        actionsCell.insertBefore(totalStockEl, actionsCell.firstChild);
      }
    }

    if (totalStockEl) {
      const stockClass =
        totalStock === 0 ? "zero" : totalStock < 10 ? "low" : "good";
      totalStockEl.innerHTML = `<span class="total-stock-badge ${stockClass}">Total: ${totalStock}</span>`;
    }
  }

  // Show success feedback when sizes are saved
  function showSaveSuccessFeedback(row) {
    const selectSizesBtn = row.querySelector(".btn-select-sizes");
    if (selectSizesBtn) {
      const originalText = selectSizesBtn.innerHTML;
      selectSizesBtn.innerHTML = '<i data-lucide="check"></i>Saved!';
      selectSizesBtn.classList.add("success-state");

      setTimeout(() => {
        selectSizesBtn.innerHTML = originalText;
        selectSizesBtn.classList.remove("success-state");
        if (window.lucide) {
          lucide.createIcons();
        }
      }, 2000);
    }
  }

  // Enhanced total stock calculation for all variants
  window.updateTotalStock = function () {
    const rows = document.querySelectorAll("#variantTableBody tr");
    let totalStock = 0;

    rows.forEach((row) => {
      const sizeInputs = row.querySelectorAll(".size-stock-input");
      let rowTotal = 0;

      sizeInputs.forEach((input) => {
        rowTotal += parseInt(input.value || "0", 10);
      });

      totalStock += rowTotal;

      // Update row display
      updateRowTotalStock(
        row,
        Array.from(sizeInputs).map((input) => ({
          size: input.dataset.size,
          stock: parseInt(input.value || "0", 10),
        }))
      );
    });

    // Update simple total stock display
    updateSimpleTotalStockDisplay(totalStock);
  };

  // Update simple total stock display
  function updateSimpleTotalStockDisplay(total) {
    const totalStockEl = document.getElementById("totalStockDisplay");
    if (totalStockEl) {
      totalStockEl.textContent = total;
    }
  }

  // Enhanced Features Implementation

  // Bulk Stock Management
  const bulkStockBtn = document.getElementById("bulkStockBtn");
  const bulkStockModal = document.getElementById("bulkStockModal");
  const bulkModalClose = document.getElementById("bulkModalClose");
  const bulkModalCancel = document.getElementById("bulkModalCancel");
  const bulkModalApply = document.getElementById("bulkModalApply");

  if (bulkStockBtn) {
    bulkStockBtn.addEventListener("click", openBulkStockModal);
  }

  if (bulkModalClose)
    bulkModalClose.addEventListener("click", closeBulkStockModal);
  if (bulkModalCancel)
    bulkModalCancel.addEventListener("click", closeBulkStockModal);
  if (bulkModalApply) bulkModalApply.addEventListener("click", applyBulkStock);

  // Bulk modal radio button handling
  document.addEventListener("change", function (e) {
    if (e.target.name === "bulkType") {
      const bulkSizeInputs = document.getElementById("bulkSizeInputs");
      if (e.target.value === "bySize") {
        bulkSizeInputs.style.display = "block";
        populateBulkSizeInputs();
      } else {
        bulkSizeInputs.style.display = "none";
      }
    }
  });

  function openBulkStockModal() {
    if (!bulkStockModal) return;
    bulkStockModal.classList.add("active");
  }

  function closeBulkStockModal() {
    if (!bulkStockModal) return;
    bulkStockModal.classList.remove("active");
  }

  function populateBulkSizeInputs() {
    const container = document.getElementById("bulkSizeInputs");
    if (!container) return;

    // Get all unique sizes from all variants
    const allSizes = new Set();
    document.querySelectorAll(".size-stock-input").forEach((input) => {
      allSizes.add(input.dataset.size);
    });

    container.innerHTML = "";
    Array.from(allSizes)
      .sort()
      .forEach((size) => {
        const group = document.createElement("div");
        group.className = "bulk-size-input-group";

        const label = document.createElement("label");
        label.className = "bulk-size-label";
        label.textContent = size;

        const input = document.createElement("input");
        input.type = "number";
        input.min = "0";
        input.className = "bulk-input";
        input.dataset.size = size;
        input.placeholder = "Stock for " + size;

        group.appendChild(label);
        group.appendChild(input);
        container.appendChild(group);
      });
  }

  function applyBulkStock() {
    const bulkType = document.querySelector(
      'input[name="bulkType"]:checked'
    )?.value;

    if (bulkType === "all") {
      const stockValue =
        parseInt(document.getElementById("bulkAllStock").value) || 0;
      document.querySelectorAll(".size-stock-input").forEach((input) => {
        input.value = stockValue;
      });
    } else if (bulkType === "bySize") {
      const sizeInputs = document.querySelectorAll(
        "#bulkSizeInputs .bulk-input"
      );
      sizeInputs.forEach((bulkInput) => {
        const size = bulkInput.dataset.size;
        const stockValue = parseInt(bulkInput.value) || 0;
        document
          .querySelectorAll(`.size-stock-input[data-size="${size}"]`)
          .forEach((input) => {
            input.value = stockValue;
          });
      });
    } else if (bulkType === "percentage") {
      const percentage =
        parseFloat(document.getElementById("bulkPercentage").value) || 100;
      document.querySelectorAll(".size-stock-input").forEach((input) => {
        const currentValue = parseInt(input.value) || 0;
        const newValue = Math.round(currentValue * (percentage / 100));
        input.value = Math.max(0, newValue);
      });
    }

    // Update totals and close modal
    if (typeof window.updateTotalStock === "function") {
      window.updateTotalStock();
    }
    closeBulkStockModal();
    showNotification("Bulk stock update applied successfully!", "success");
  }

  // Stock Validation
  const validateStockBtn = document.getElementById("validateStockBtn");
  const validationModal = document.getElementById("validationModal");
  const validationModalClose = document.getElementById("validationModalClose");
  const validationModalClose2 = document.getElementById(
    "validationModalClose2"
  );

  if (validateStockBtn) {
    validateStockBtn.addEventListener("click", validateStock);
  }

  if (validationModalClose)
    validationModalClose.addEventListener("click", closeValidationModal);
  if (validationModalClose2)
    validationModalClose2.addEventListener("click", closeValidationModal);

  function validateStock() {
    const results = performStockValidation();
    displayValidationResults(results);
    validationModal.classList.add("active");
  }

  function closeValidationModal() {
    if (!validationModal) return;
    validationModal.classList.remove("active");
  }

  function performStockValidation() {
    const results = {
      errors: [],
      warnings: [],
      info: [],
      success: [],
    };

    const rows = document.querySelectorAll("#variantTableBody tr");
    let totalVariants = 0;
    let variantsWithStock = 0;
    let totalStock = 0;
    let emptyVariants = [];
    let lowStockVariants = [];

    rows.forEach((row, index) => {
      const rowNum = index + 1;
      const sku = row.querySelector('input[name^="sku_"]')?.value?.trim();
      const color = row.querySelector('input[name^="color_"]')?.value?.trim();
      const sizeInputs = row.querySelectorAll(".size-stock-input");

      totalVariants++;

      if (!sku && !color && sizeInputs.length === 0) {
        emptyVariants.push(rowNum);
        return;
      }

      let rowStock = 0;
      sizeInputs.forEach((input) => {
        const stock = parseInt(input.value) || 0;
        rowStock += stock;
      });

      totalStock += rowStock;

      if (rowStock > 0) {
        variantsWithStock++;
      } else if (sku || color) {
        lowStockVariants.push({ row: rowNum, sku, color });
      }

      // Check for missing required fields
      if (sizeInputs.length > 0 && !sku) {
        results.warnings.push(`Variant ${rowNum}: Has sizes but missing SKU`);
      }

      if (sizeInputs.length > 0 && !color) {
        results.warnings.push(`Variant ${rowNum}: Has sizes but missing color`);
      }
    });

    // Generate results
    if (emptyVariants.length > 0) {
      results.info.push(
        `Empty variants found: Row(s) ${emptyVariants.join(
          ", "
        )} - these will be ignored`
      );
    }

    if (lowStockVariants.length > 0) {
      results.warnings.push(
        `${lowStockVariants.length} variant(s) have no stock but have SKU/color defined`
      );
    }

    if (totalStock === 0) {
      results.errors.push("No stock quantities set for any variant");
    } else {
      results.success.push(
        `Total stock: ${totalStock} units across ${variantsWithStock} variant(s)`
      );
    }

    if (variantsWithStock > 0) {
      results.success.push(
        `${variantsWithStock} out of ${totalVariants} variants have stock`
      );
    }

    // Check for duplicate SKUs
    const skus = [];
    rows.forEach((row, index) => {
      const sku = row.querySelector('input[name^="sku_"]')?.value?.trim();
      if (sku) {
        if (skus.includes(sku)) {
          results.errors.push(`Duplicate SKU found: "${sku}"`);
        } else {
          skus.push(sku);
        }
      }
    });

    return results;
  }

  function displayValidationResults(results) {
    const container = document.getElementById("validationResults");
    if (!container) return;

    container.innerHTML = "";

    const sections = [
      {
        type: "error",
        title: "Errors",
        items: results.errors,
        icon: "alert-circle",
      },
      {
        type: "warning",
        title: "Warnings",
        items: results.warnings,
        icon: "alert-triangle",
      },
      {
        type: "success",
        title: "Success",
        items: results.success,
        icon: "check-circle",
      },
      { type: "info", title: "Information", items: results.info, icon: "info" },
    ];

    sections.forEach((section) => {
      if (section.items.length > 0) {
        const sectionEl = document.createElement("div");
        sectionEl.className = `validation-section ${section.type}`;

        const header = document.createElement("div");
        header.className = "validation-header";
        header.innerHTML = `
          <i data-lucide="${section.icon}" class="validation-icon"></i>
          <h4 class="validation-title">${section.title} (${section.items.length})</h4>
        `;

        const content = document.createElement("div");
        content.className = "validation-content";

        if (section.items.length === 1) {
          content.textContent = section.items[0];
        } else {
          const list = document.createElement("ul");
          list.className = "validation-list";
          section.items.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;
            list.appendChild(li);
          });
          content.appendChild(list);
        }

        sectionEl.appendChild(header);
        sectionEl.appendChild(content);
        container.appendChild(sectionEl);
      }
    });

    // Initialize Lucide icons for validation results
    if (window.lucide) {
      lucide.createIcons();
    }
  }

  // Enhanced Variant Counter
  function updateVariantStats() {
    const rows = document.querySelectorAll("#variantTableBody tr");
    const variantCount = rows.length;
    const variantCountEl = document.getElementById("variantCount");
    const variantPluralEl = document.getElementById("variantPlural");

    if (variantCountEl) {
      variantCountEl.textContent = variantCount;
    }

    if (variantPluralEl) {
      variantPluralEl.style.display = variantCount === 1 ? "none" : "inline";
    }

    // Update total stock display
    let totalStock = 0;
    document.querySelectorAll(".size-stock-input").forEach((input) => {
      totalStock += parseInt(input.value) || 0;
    });

    const totalStockEl = document.getElementById("totalStockDisplay");
    if (totalStockEl) {
      totalStockEl.textContent = totalStock;
    }
  }

  // Notification System
  function showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <i data-lucide="${getNotificationIcon(type)}"></i>
        <span>${message}</span>
      </div>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.classList.add("show");
    }, 100);

    // Remove after delay
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);

    // Initialize Lucide icons
    if (window.lucide) {
      lucide.createIcons();
    }
  }

  function getNotificationIcon(type) {
    const icons = {
      success: "check-circle",
      error: "alert-circle",
      warning: "alert-triangle",
      info: "info",
    };
    return icons[type] || "info";
  }

  // Enhanced updateTotalStock function
  const originalUpdateTotalStock = window.updateTotalStock;
  window.updateTotalStock = function () {
    if (originalUpdateTotalStock) {
      originalUpdateTotalStock();
    }
    updateVariantStats();
  };

  // Initialize enhanced features
  setTimeout(() => {
    updateVariantStats();
    if (typeof window.updateTotalStock === "function") {
      window.updateTotalStock();
    }
  }, 500);

  // Initialize Lucide icons for the page
  if (window.lucide) {
    lucide.createIcons();
  }

  console.log("Enhanced stock management features initialized");
});

// Global form save handler for the template onclick
function handleFormSave(event) {
  if (event) {
    event.preventDefault();
  }
  
  // Call the existing form submission handler
  if (typeof handleFormSubmission === 'function') {
    handleFormSubmission();
  } else {
    console.error('handleFormSubmission function not found');
  }
}

// Add spin animation CSS
const spinStyle = document.createElement('style');
spinStyle.textContent = `
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;
document.head.appendChild(spinStyle);