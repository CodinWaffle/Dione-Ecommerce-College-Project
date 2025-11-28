
// Enhanced size selection functionality with improved UI/UX
document.addEventListener("DOMContentLoaded", function () {
  console.log("Enhanced size selection modal loaded");

  const AVAILABLE_SIZE_GROUPS = [
    {
      name: "Clothing",
      hint: "Shirts, tops, dresses",
      icon: "👕",
      sizes: ["XS", "S", "M", "L", "XL", "XXL", "One size", "Free size"],
    },
    {
      name: "Shoes",
      hint: "US / EU shoe sizes",
      icon: "👟",
      sizes: [
        "US 5", "US 6", "US 7", "US 8", "US 9", "US 10", "US 11",
        "EU 36", "EU 37", "EU 38", "EU 39", "EU 40", "EU 41", "EU 42",
      ],
    },
    {
      name: "Rings",
      hint: "Ring sizes",
      icon: "💍",
      sizes: [
        "Ring 4", "Ring 5", "Ring 6", "Ring 7", "Ring 8", "Ring 9", "Ring 10",
      ],
    },
    {
      name: "Accessories",
      hint: "Waist, custom sizes",
      icon: "👜",
      sizes: ["Waist 28", "Waist 30", "Waist 32", "Waist 34", "Waist 36", "Other"],
    },
  ];

  const sizeModal = document.getElementById("sizeSelectModal");
  const sizeOptionsContainer = document.getElementById("sizeOptionsContainer");
  const sizeModalSave = document.getElementById("sizeModalSave");
  const sizeModalCancel = document.getElementById("sizeModalCancel");
  const sizeModalClose = document.getElementById("sizeModalClose");

  let currentSizeModalRow = null;

  function openSizeModalForRow(row) {
    if (!sizeModal || !sizeOptionsContainer) return;
    currentSizeModalRow = row;
    sizeOptionsContainer.innerHTML = "";

    // Get existing size stocks
    const existingSizeInputs = row.querySelectorAll(".size-stock-input");
    const existingMap = {};
    existingSizeInputs.forEach((inp) => {
      const s = inp.dataset.size;
      existingMap[s] = inp.value || "0";
    });

    // Create enhanced size selection interface
    const headerDiv = document.createElement("div");
    headerDiv.className = "size-selection-header";
    headerDiv.innerHTML = `
      <div class="size-selection-intro">
        <h3>📦 Select Product Sizes</h3>
        <p>Choose the sizes available for this variant and set stock quantities</p>
      </div>
      <div class="size-selection-stats">
        <span class="stat-badge" id="selectedSizesCount">0 sizes selected</span>
        <span class="stat-badge" id="totalStockCount">0 total stock</span>
      </div>
    `;
    sizeOptionsContainer.appendChild(headerDiv);

    // Render size groups with enhanced design
    AVAILABLE_SIZE_GROUPS.forEach((group) => {
      const groupContainer = document.createElement("div");
      groupContainer.className = "enhanced-size-group";

      const groupHeader = document.createElement("div");
      groupHeader.className = "enhanced-group-header";
      groupHeader.innerHTML = `
        <div class="group-info">
          <span class="group-icon">${group.icon}</span>
          <div class="group-text">
            <h4>${group.name}</h4>
            <p>${group.hint}</p>
          </div>
        </div>
        <div class="group-toggle">
          <button type="button" class="toggle-btn" data-group="${group.name}">
            <i data-lucide="chevron-down"></i>
          </button>
        </div>
      `;

      const groupContent = document.createElement("div");
      groupContent.className = "enhanced-group-content";
      groupContent.id = `group-${group.name.toLowerCase()}`;

      const sizesGrid = document.createElement("div");
      sizesGrid.className = "enhanced-sizes-grid";

      group.sizes.forEach((size) => {
        const sizeCard = document.createElement("div");
        sizeCard.className = "enhanced-size-card";
        sizeCard.dataset.size = size;

        if (existingMap[size] !== undefined) {
          sizeCard.classList.add("selected");
        }

        sizeCard.innerHTML = `
          <div class="size-card-header">
            <span class="size-name">${size}</span>
            <div class="size-check">
              <i data-lucide="check"></i>
            </div>
          </div>
          <div class="size-card-body">
            <input type="number" 
                   class="stock-input" 
                   placeholder="Stock" 
                   min="0" 
                   value="${existingMap[size] || ''}"
                   data-size="${size}"
                   ${!existingMap[size] ? 'style="display: none;"' : ''}>
          </div>
        `;

        // Enhanced click handler
        sizeCard.addEventListener("click", (e) => {
          if (e.target.classList.contains("stock-input")) return;

          sizeCard.classList.toggle("selected");
          const stockInput = sizeCard.querySelector(".stock-input");
          
          if (sizeCard.classList.contains("selected")) {
            stockInput.style.display = "block";
            if (!stockInput.value) {
              stockInput.value = "1";
            }
            setTimeout(() => stockInput.focus(), 100);
          } else {
            stockInput.style.display = "none";
            stockInput.value = "";
          }
          
          updateModalStats();
        });

        // Stock input handler
        const stockInput = sizeCard.querySelector(".stock-input");
        stockInput.addEventListener("input", updateModalStats);

        sizesGrid.appendChild(sizeCard);
      });

      groupContent.appendChild(sizesGrid);
      groupContainer.appendChild(groupHeader);
      groupContainer.appendChild(groupContent);
      sizeOptionsContainer.appendChild(groupContainer);

      // Group toggle functionality
      const toggleBtn = groupHeader.querySelector(".toggle-btn");
      toggleBtn.addEventListener("click", () => {
        groupContent.classList.toggle("collapsed");
        const icon = toggleBtn.querySelector("i");
        icon.setAttribute("data-lucide", 
          groupContent.classList.contains("collapsed") ? "chevron-right" : "chevron-down"
        );
        if (window.lucide) lucide.createIcons();
      });
    });

    // Add custom size section
    const customSection = document.createElement("div");
    customSection.className = "custom-size-section";
    customSection.innerHTML = `
      <div class="custom-section-header">
        <h4>✨ Add Custom Size</h4>
        <p>Create your own size if not listed above</p>
      </div>
      <div class="custom-input-group">
        <input type="text" 
               class="custom-size-name" 
               placeholder="e.g., 7.5 UK, 29W, Medium-Large"
               maxlength="20">
        <input type="number" 
               class="custom-size-stock" 
               placeholder="Stock" 
               min="0">
        <button type="button" class="add-custom-btn">
          <i data-lucide="plus"></i>
          Add
        </button>
      </div>
      <div class="custom-sizes-list" id="customSizesList"></div>
    `;
    sizeOptionsContainer.appendChild(customSection);

    // Custom size functionality
    const customNameInput = customSection.querySelector(".custom-size-name");
    const customStockInput = customSection.querySelector(".custom-size-stock");
    const addCustomBtn = customSection.querySelector(".add-custom-btn");
    const customSizesList = customSection.querySelector(".custom-sizes-list");

    addCustomBtn.addEventListener("click", addCustomSize);
    customNameInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") addCustomSize();
    });

    function addCustomSize() {
      const sizeName = customNameInput.value.trim();
      const stock = parseInt(customStockInput.value) || 0;

      if (!sizeName) {
        alert("Please enter a size name");
        return;
      }

      // Check if size already exists
      if (document.querySelector(`[data-size="${sizeName}"]`)) {
        alert("This size already exists");
        return;
      }

      const customSizeCard = document.createElement("div");
      customSizeCard.className = "custom-size-card selected";
      customSizeCard.dataset.size = sizeName;
      customSizeCard.innerHTML = `
        <span class="custom-size-name">${sizeName}</span>
        <input type="number" 
               class="stock-input" 
               value="${stock}" 
               min="0" 
               data-size="${sizeName}">
        <button type="button" class="remove-custom" title="Remove">
          <i data-lucide="x"></i>
        </button>
      `;

      customSizeCard.querySelector(".remove-custom").addEventListener("click", () => {
        customSizeCard.remove();
        updateModalStats();
      });

      customSizeCard.querySelector(".stock-input").addEventListener("input", updateModalStats);

      customSizesList.appendChild(customSizeCard);
      
      customNameInput.value = "";
      customStockInput.value = "";
      
      updateModalStats();
      
      if (window.lucide) lucide.createIcons();
    }

    // Load existing custom sizes
    const existingCustomSizes = Object.keys(existingMap).filter((size) => {
      return !AVAILABLE_SIZE_GROUPS.some((group) => group.sizes.includes(size));
    });

    existingCustomSizes.forEach((customSize) => {
      customNameInput.value = customSize;
      customStockInput.value = existingMap[customSize];
      addCustomSize();
    });

    function updateModalStats() {
      const selectedCards = sizeOptionsContainer.querySelectorAll(".enhanced-size-card.selected, .custom-size-card");
      const totalStock = Array.from(selectedCards).reduce((sum, card) => {
        const input = card.querySelector(".stock-input");
        return sum + (parseInt(input.value) || 0);
      }, 0);

      document.getElementById("selectedSizesCount").textContent = 
        `${selectedCards.length} size${selectedCards.length !== 1 ? 's' : ''} selected`;
      document.getElementById("totalStockCount").textContent = 
        `${totalStock} total stock`;
    }

    // Initialize Lucide icons
    if (window.lucide) {
      lucide.createIcons();
    }

    updateModalStats();
    sizeModal.classList.add("active");
  }

  function closeSizeModal() {
    if (sizeModal) {
      sizeModal.classList.remove("active");
    }
    currentSizeModalRow = null;
  }

  function saveSizeModal() {
    if (!currentSizeModalRow) return;

    const selectedCards = sizeOptionsContainer.querySelectorAll(
      ".enhanced-size-card.selected, .custom-size-card"
    );

    const sizeGroup = currentSizeModalRow.querySelector(".variant-size-group");
    const sizeSummary = currentSizeModalRow.querySelector(".variant-size-summary");
    const sizeContainer = currentSizeModalRow.querySelector(".size-stock-container");

    // Clear existing inputs
    const existing = Array.from(currentSizeModalRow.querySelectorAll(".size-stock-input"));
    existing.forEach((e) => e.remove());

    if (sizeGroup) sizeGroup.innerHTML = "";
    if (sizeContainer) sizeContainer.innerHTML = "";

    const stocks = [];

    selectedCards.forEach((card) => {
      const sizeName = card.dataset.size;
      const stockInput = card.querySelector(".stock-input");
      const stockValue = parseInt(stockInput?.value || "0", 10) || 0;

      stocks.push({ size: sizeName, stock: stockValue });
      addSizeToRow(sizeName, stockValue, sizeGroup, sizeContainer);
    });

    // Update summary
    if (sizeSummary) {
      if (stocks.length === 0) {
        sizeSummary.innerHTML = '<span class="no-sizes">No sizes selected</span>';
      } else {
        const totalStock = stocks.reduce((sum, s) => sum + s.stock, 0);
        const summaryHtml = stocks
          .map((s) => {
            const stockClass = s.stock === 0 ? "out-of-stock" : s.stock < 5 ? "low-stock" : "in-stock";
            return `<span class="size-summary-item ${stockClass}">${s.size}: ${s.stock}</span>`;
          })
          .join(" • ");

        sizeSummary.innerHTML = `
          <div class="size-summary-header">
            <strong>${stocks.length} size${stocks.length > 1 ? "s" : ""} selected (Total: ${totalStock})</strong>
          </div>
          <div class="size-summary-details">${summaryHtml}</div>
        `;
      }
    }

    // Update row total stock
    updateRowTotalStock(currentSizeModalRow, stocks);

    // Update global total
    if (typeof window.updateTotalStock === "function") {
      window.updateTotalStock();
    }

    // Show success feedback
    showSaveSuccessFeedback(currentSizeModalRow);

    closeSizeModal();
  }

  function addSizeToRow(sizeName, stockValue, sizeGroup, sizeContainer) {
    if (sizeGroup) {
      const hiddenInput = document.createElement("input");
      hiddenInput.type = "hidden";
      hiddenInput.className = "size-stock-input";
      hiddenInput.dataset.size = sizeName;
      hiddenInput.value = stockValue;
      sizeGroup.appendChild(hiddenInput);
    }

    if (sizeContainer) {
      const item = document.createElement("div");
      item.className = "size-stock-item";
      item.innerHTML = `
        <span class="size-label">${sizeName}</span>
        <input type="number" 
               min="0" 
               class="size-stock-input" 
               data-size="${sizeName}" 
               value="${stockValue}">
      `;

      item.querySelector(".size-stock-input").addEventListener("input", () => {
        if (typeof window.updateTotalStock === "function") {
          window.updateTotalStock();
        }
      });

      sizeContainer.appendChild(item);
    }
  }

  function updateRowTotalStock(row, stocks) {
    const totalStock = stocks.reduce((sum, s) => sum + s.stock, 0);
    let totalStockEl = row.querySelector(".row-total-stock .total-stock-badge");

    if (totalStockEl) {
      const stockClass = totalStock === 0 ? "zero" : totalStock < 10 ? "low" : "good";
      totalStockEl.className = `total-stock-badge ${stockClass}`;
      totalStockEl.textContent = `Total: ${totalStock}`;
    }
  }

  function showSaveSuccessFeedback(row) {
    const selectSizesBtn = row.querySelector(".btn-select-sizes");
    if (selectSizesBtn) {
      const originalText = selectSizesBtn.innerHTML;
      selectSizesBtn.innerHTML = '<i data-lucide="check"></i>Saved!';
      selectSizesBtn.classList.add("success-state");

      setTimeout(() => {
        selectSizesBtn.innerHTML = originalText;
        selectSizesBtn.classList.remove("success-state");
        if (window.lucide) lucide.createIcons();
      }, 2000);
    }
  }

  // Event listeners
  if (sizeModalSave) sizeModalSave.addEventListener("click", saveSizeModal);
  if (sizeModalCancel) sizeModalCancel.addEventListener("click", closeSizeModal);
  if (sizeModalClose) sizeModalClose.addEventListener("click", closeSizeModal);

  if (sizeModal) {
    sizeModal.addEventListener("click", (e) => {
      if (e.target === sizeModal) closeSizeModal();
    });
  }

  // Delegate click for Select Sizes buttons
  document.addEventListener("click", function (e) {
    const btn = e.target.closest(".btn-select-sizes");
    if (!btn) return;
    const row = btn.closest("tr");
    if (!row) return;
    openSizeModalForRow(row);
  });

  console.log("Enhanced size selection modal initialized");
});