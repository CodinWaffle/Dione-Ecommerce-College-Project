// Form submission and data persistence for add_product_stocks page
document.addEventListener("DOMContentLoaded", function () {
  console.log("add_product_stocks.js loaded");

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
        stockInput.placeholder = "Stock";
        stockInput.className = "stock-input-small";
        stockInput.dataset.size = sz;
        stockInput.value = existingMap[sz] || "";
        
        if (!existingMap[sz]) {
          stockInput.style.display = "none";
        }

        // Handle box click to select/deselect
        wrapper.addEventListener("click", (e) => {
          if (e.target === stockInput) return; // Don't toggle when clicking input
          
          wrapper.classList.toggle("selected");
          if (wrapper.classList.contains("selected")) {
            stockInput.style.display = "block";
            stockInput.focus();
          } else {
            stockInput.style.display = "none";
            stockInput.value = "";
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
    const existingCustomSizes = Object.keys(existingMap).filter(size => {
      return !AVAILABLE_SIZE_GROUPS.some(group => group.sizes.includes(size));
    });

    existingCustomSizes.forEach(customSize => {
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

    // Update visible summary
    if (sizeSummary) {
      if (stocks.length === 0) {
        sizeSummary.textContent = "No sizes selected";
      } else {
        sizeSummary.textContent = stocks
          .map((s) => `${s.size} (${s.stock})`)
          .join(", ");
      }
    }

    // Trigger total update
    if (typeof window.updateTotalStock === "function") {
      window.updateTotalStock();
    }

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
