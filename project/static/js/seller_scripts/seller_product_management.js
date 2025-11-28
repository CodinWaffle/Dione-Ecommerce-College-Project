document.addEventListener("DOMContentLoaded", function () {
  console.log("[v0] Product management script loaded");

  // Initialize Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // DOM Elements
  const addProductBtn = document.getElementById("addProductBtn");
  const productModal = document.getElementById("productModal");
  const productDetailModal = document.getElementById("productDetailModal");
  const closeProductDetailBtn = document.getElementById(
    "closeProductDetailModal"
  );
  const closeModalBtns = document.querySelectorAll(".close-btn");
  const productForm = document.getElementById("productForm");
  const imageUpload = document.getElementById("imageUpload");
  const imagePreview = document.getElementById("imagePreview");
  const searchInput = document.querySelector(".search-box input");
  const categoryFilter = document.getElementById("filterCategory");
  const statusFilter = document.getElementById("filterStatus");

  // Move filters closer to the search box for tighter layout (keeps DOM structure but reorders)
  try {
    const controls = document.querySelector(".product-controls");
    const searchBox = controls?.querySelector(".search-box");
    const filterGroup = controls?.querySelector(".filter-group");
    if (controls && searchBox && filterGroup) {
      // insert filterGroup immediately after searchBox
      searchBox.parentNode.insertBefore(filterGroup, searchBox.nextSibling);
    }
  } catch (err) {
    // if DOM differs, ignore
  }

  // Wire search + filters to filtering function
  if (searchInput) {
    searchInput.addEventListener("input", filterProducts);
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        filterProducts();
      }
    });
  }
  if (categoryFilter) categoryFilter.addEventListener("change", filterProducts);
  if (statusFilter) statusFilter.addEventListener("change", filterProducts);

  console.log("[v0] Add Product Button found:", addProductBtn);
  if (!addProductBtn) {
    console.error(
      "[v0] ERROR: addProductBtn element not found! Searching alternatives..."
    );
    console.log(
      "[v0] All buttons on page:",
      document.querySelectorAll("button")
    );
  }

  const preloaded = window.__SELLER_PRODUCTS__ || [];
  // Normalize preloaded server objects to the shape the frontend expects
  function normalizeProduct(p) {
    if (!p) return null;
    const totalStock =
      p.total_stock != null ? p.total_stock : p.stock != null ? p.stock : 0;

    // Determine status based on backend data, not just stock
    let displayStatus;
    if (p.is_draft) {
      displayStatus = "draft";
    } else if (totalStock === 0) {
      displayStatus = "Not Active"; // Zero stock = Not Active
    } else if (p.status === "active") {
      displayStatus = "Active"; // Has stock and active = Active
    } else {
      displayStatus = p.status || "draft";
    }

    return {
      id: p.id,
      name: p.name || p.productName || "",
      image: p.primary_image || p.image || "/static/image/banner.png",
      category: p.category || "",
      subcategory: p.subcategory || p.subCategory || "",
      price: p.price || p.amount || 0,
      stock: totalStock,
      total_stock: totalStock,
      status: displayStatus,
      raw: p,
    };
  }

  let products = Array.isArray(preloaded)
    ? preloaded.map(normalizeProduct).filter(Boolean)
    : [];

  // Refresh products from server to ensure data is current
  async function refreshProductsFromServer() {
    try {
      console.log("Refreshing products from server...");
      const response = await fetch("/seller/products");
      if (response.ok) {
        // The server response contains the full HTML page, but we can extract the JSON data
        const text = await response.text();
        const match = text.match(
          /window\.__SELLER_PRODUCTS__\s*=\s*(\[.*?\]);/s
        );
        if (match) {
          const serverProducts = JSON.parse(match[1]);
          products = serverProducts.map(normalizeProduct).filter(Boolean);
          renderProducts(products);
          console.log("Products refreshed from server:", products.length);
        }
      }
    } catch (error) {
      console.warn("Could not refresh products from server:", error);
    }
  }

  // If no preloaded data, try to parse server-rendered table rows so JS doesn't wipe them.
  function parseServerRenderedRows() {
    const rows = Array.from(document.querySelectorAll("#productTableBody tr"));
    const parsed = rows
      .map((row) => {
        const id = parseInt(row.dataset.id) || null;
        const nameEl = row.querySelector(".product-name");
        const imgEl = row.querySelector(".product-image");
        const tds = row.querySelectorAll("td");
        const category = (tds[2] && tds[2].textContent.trim()) || "";
        const subcategory = (tds[3] && tds[3].textContent.trim()) || "";
        const priceText =
          (tds[4] && tds[4].textContent.replace(/[^0-9.\-]/g, "").trim()) ||
          "0";
        const price = parseFloat(priceText) || 0;
        const stockText = (tds[5] && tds[5].textContent.trim()) || "";
        const stock =
          stockText === "—" || stockText === ""
            ? null
            : parseInt(stockText) || 0;
        const statusEl = row.querySelector(".status-badge");
        const status = statusEl ? statusEl.textContent.trim() : "";

        return {
          id: id,
          name: nameEl ? nameEl.textContent.trim() : "",
          primary_image: imgEl ? imgEl.src : "/static/image/banner.png",
          category: category,
          subcategory: subcategory === "—" ? "" : subcategory,
          price: price,
          total_stock: stock,
          status: status,
        };
      })
      .filter((p) => p.id !== null);
    return parsed;
  }

  // If no products from server data, parse table rows
  if (products.length === 0) {
    products = parseServerRenderedRows().map(normalizeProduct).filter(Boolean);
  }

  // Refresh products from server when page loads to ensure current data
  setTimeout(refreshProductsFromServer, 100);

  // Tab elements
  const tabAll = document.getElementById("tabAll");
  const tabOut = document.getElementById("tabOut");
  const tabActive = document.getElementById("tabActive");

  // Modal accessibility & UX helpers
  function _focusFirstInput(modal) {
    if (!modal) return;
    const focusable = modal.querySelectorAll(
      'input, button, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable && focusable.length) {
      try {
        focusable[0].focus();
      } catch (e) {}
    }
  }

  function _onModalActiveChange(modal) {
    if (!modal) return;
    const isActive = modal.classList.contains("active");
    modal.setAttribute("aria-hidden", isActive ? "false" : "true");
    if (isActive) {
      _focusFirstInput(modal);
    }
  }

  // Observe modal class changes to apply accessible behaviour
  [
    productDetailModal,
    document.getElementById("variantStockModal"),
    productModal,
  ].forEach((m) => {
    if (!m) return;
    // Ensure dialog semantics
    m.setAttribute("role", "dialog");
    m.setAttribute("aria-modal", "true");
    m.setAttribute(
      "aria-hidden",
      m.classList.contains("active") ? "false" : "true"
    );
    const obs = new MutationObserver(() => _onModalActiveChange(m));
    obs.observe(m, { attributes: true, attributeFilter: ["class"] });
  });

  // Close modals on Escape key for faster UX
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" || e.key === "Esc") {
      const modalList = [
        productDetailModal,
        document.getElementById("variantStockModal"),
        productModal,
      ];
      modalList.forEach((mm) => {
        if (mm && mm.classList.contains("active")) {
          mm.classList.remove("active");
          mm.setAttribute("aria-hidden", "true");
        }
      });
    }
  });

  function setActiveTab(tabEl) {
    document.querySelectorAll(".seller-nav-tabs .tab").forEach((t) => {
      t.classList.remove("active");
      t.setAttribute("aria-selected", "false");
    });
    if (tabEl) {
      tabEl.classList.add("active");
      tabEl.setAttribute("aria-selected", "true");
    }
  }

  function updateCounts() {
    const total = products.length;
    const out = products.filter(
      (p) => p.status === "Not Active" || p.stock === 0 || p.total_stock === 0
    ).length;
    // Active listings should be products that show as "Active"
    const active = products.filter((p) => p.status === "Active").length;
    document.getElementById("countAll").textContent = total;
    document.getElementById("countOut").textContent = out;
    document.getElementById("countActive").textContent = active;
  }

  function handleImageFiles(files) {
    Array.from(files).forEach((file) => {
      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const img = document.createElement("img");
          img.src = e.target.result;
          img.className = "preview-image";
          imagePreview.appendChild(img);
        };
        reader.readAsDataURL(file);
      }
    });
  }

  function getSelectedIds() {
    return Array.from(document.querySelectorAll(".row-select:checked")).map(
      (cb) => parseInt(cb.dataset.id)
    );
  }

  function filterProducts() {
    const searchTerm = (searchInput?.value || "").toLowerCase();
    const categoryValue = categoryFilter?.value || "";
    const statusValue = statusFilter?.value || "";

    const filteredProducts = products.filter((product) => {
      const matchesSearch =
        !searchTerm ||
        product.name.toLowerCase().includes(searchTerm) ||
        String(product.id).includes(searchTerm);
      const matchesCategory =
        !categoryValue || product.category === categoryValue;
      let matchesStatus = true;
      if (statusValue) {
        if (statusValue === "out-of-stock") {
          matchesStatus = product.status === "Not Active";
        } else if (statusValue === "active") {
          matchesStatus = product.status === "Active";
        } else if (statusValue === "draft") {
          matchesStatus = product.status === "draft";
        } else {
          matchesStatus = product.status === statusValue;
        }
      }
      return matchesSearch && matchesCategory && matchesStatus;
    });

    renderProducts(filteredProducts);
  }

  function renderProducts(productsToRender) {
    const tbody = document.getElementById("productTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    productsToRender.forEach((product) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
                <td class="col-center"><input type="checkbox" class="row-select" data-id="${
                  product.id
                }"></td>
                <td class="col-left">
                    <div class="product-info">
                        <img src="${
                          product.image || "/static/image/banner.png"
                        }" alt="${product.name}" class="product-image">
                        <span class="product-name">${product.name}</span>
                    </div>
                </td>
                <td class="col-center">${product.category}</td>
                <td class="col-center">${product.subcategory || "—"}</td>
                <td class="col-center">₱${
                  product.price ? parseFloat(product.price).toFixed(2) : "0.00"
                }</td>
                <td class="col-center">${
                  product.total_stock != null
                    ? product.total_stock
                    : product.stock != null
                    ? product.stock
                    : "—"
                }</td>
                <td class="col-center"><span class="status-badge status-${
                  product.status
                }">${product.status}</span></td>
                <td class="col-center">
                    <div class="action-buttons">
                        <button class="btn-icon open-variants" data-id="${
                          product.id
                        }" title="Manage variant stocks">
                            <i data-lucide="layers"></i>
                        </button>
                        <button class="btn-icon edit-product" data-id="${
                          product.id
                        }" title="Edit product details">
                            <i data-lucide="edit"></i><span>Edit</span>
                        </button>
                        <button class="btn-icon delete-product" data-id="${
                          product.id
                        }" title="Delete product">
                            <i data-lucide="trash-2"></i>
                        </button>
                    </div>
                </td>
            `;
      tbody.appendChild(tr);
    });

    if (window.lucide) {
      lucide.createIcons();
    }
    updateCounts();

    // Update table footer counts (if footer component exists)
    try {
      const footer = document.querySelector(".component-table-footer");
      if (footer) {
        const showingEl = footer.querySelector(".tf-showing");
        const totalEl = footer.querySelector(".tf-total");
        const visible = productsToRender ? productsToRender.length : 0;
        const total = products ? products.length : visible;
        if (showingEl)
          showingEl.textContent = visible > 0 ? `1-${visible}` : "0";
        if (totalEl) totalEl.textContent = total;
      }
    } catch (err) {
      // ignore footer update errors
    }
  }

  // If there were no preloaded products, parse server-rendered rows and use those
  if (!Array.isArray(products) || products.length === 0) {
    const fromDom = parseServerRenderedRows();
    if (fromDom && fromDom.length > 0)
      products = fromDom.map(normalizeProduct).filter(Boolean);
  }
  renderProducts(products);

  // sliding underline handling
  const tabsUnderline = document.querySelector(".tabs-underline");
  function positionUnderline() {
    const active = document.querySelector(".seller-nav-tabs .tab.active");
    const container = document.querySelector(".seller-nav-tabs");
    if (!tabsUnderline || !active || !container) return;
    const aRect = active.getBoundingClientRect();
    const cRect = container.getBoundingClientRect();
    const left = Math.max(0, aRect.left - cRect.left + container.scrollLeft);
    const width = Math.max(0, aRect.width);
    tabsUnderline.style.left = left + "px";
    tabsUnderline.style.width = width + "px";
  }

  // reposition on tab changes and viewport changes
  ["click", "resize", "orientationchange", "scroll"].forEach((evt) => {
    if (evt === "click") {
      document
        .querySelectorAll(".seller-nav-tabs .tab")
        .forEach((t) =>
          t.addEventListener("click", () => setTimeout(positionUnderline, 40))
        );
    } else {
      window.addEventListener(evt, positionUnderline, { passive: true });
    }
  });
  // initial position after icons render
  setTimeout(positionUnderline, 80);

  // wire tab clicks to set status filter and re-run filterProducts
  tabAll?.addEventListener("click", () => {
    setActiveTab(tabAll);
    if (statusFilter) statusFilter.value = "";
    filterProducts();
  });
  tabOut?.addEventListener("click", () => {
    setActiveTab(tabOut);
    if (statusFilter) statusFilter.value = "out-of-stock";
    filterProducts();
  });
  tabActive?.addEventListener("click", () => {
    setActiveTab(tabActive);
    if (statusFilter) statusFilter.value = "active";
    filterProducts();
  });

  if (addProductBtn) {
    console.log("[v0] Attaching click listener to Add Product button");
    addProductBtn.addEventListener("click", function (e) {
      console.log("[v0] Add Product button clicked");
      e.preventDefault();
      e.stopPropagation();

      // Navigate to add product page
      console.log("[v0] Navigating to /seller/add_product");
      window.location.href = "/seller/add_product";
    });

    // Make sure button is not disabled
    addProductBtn.disabled = false;
    addProductBtn.style.pointerEvents = "auto";
  }

  // Delete confirmation modal handlers
  const deleteModal = document.getElementById("deleteConfirmModal");
  const closeDeleteModal = document.getElementById("closeDeleteModal");
  const cancelDelete = document.getElementById("cancelDelete");
  const confirmDelete = document.getElementById("confirmDelete");

  // Close modal handlers
  [closeDeleteModal, cancelDelete].forEach((btn) => {
    if (btn) {
      btn.addEventListener("click", hideDeleteConfirmation);
    }
  });

  // Confirm delete handler
  if (confirmDelete) {
    confirmDelete.addEventListener("click", async function () {
      if (productToDelete && !isDeletingProduct) {
        isDeletingProduct = true;

        // Disable the button to prevent double clicks
        confirmDelete.disabled = true;
        confirmDelete.textContent = "Deleting...";

        try {
          const success = await deleteProduct(productToDelete.id);
          console.log("Delete operation success:", success);

          // Always hide the modal after attempting delete
          hideDeleteConfirmation();

          if (!success) {
            console.error("Delete operation failed");
          }
        } catch (error) {
          console.error("Error in delete confirmation:", error);
          hideDeleteConfirmation();
        } finally {
          // Reset button state
          isDeletingProduct = false;
          confirmDelete.disabled = false;
          confirmDelete.textContent = "Yes, Delete";
        }
      }
    });
  }

  // Close on backdrop click
  if (deleteModal) {
    deleteModal.addEventListener("click", function (e) {
      if (e.target === deleteModal) {
        hideDeleteConfirmation();
      }
    });
  } else {
    console.error("[v0] CRITICAL: addProductBtn not found - button won't work");
  }

  closeModalBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (productModal) productModal.classList.remove("active");
      if (productDetailModal) productDetailModal.classList.remove("active");
      const variantModal = document.getElementById("variantStockModal");
      if (variantModal) variantModal.classList.remove("active");
    });
  });
  document
    .getElementById("productTableBody")
    ?.addEventListener("click", function (e) {
      const openVariantsBtn = e.target.closest(".open-variants");
      const editBtn = e.target.closest(".edit-product");
      const delBtn = e.target.closest(".delete-product");

      // Open variants / stocks modal
      if (openVariantsBtn) {
        const id = parseInt(openVariantsBtn.dataset.id);
        if (!id) return;
        fetch(`/seller/product/${id}/details`)
          .then((res) => {
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
          })
          .then((data) => {
            window.__currentVariantProductId = id;
            window.__currentVariantData = Array.isArray(data.variants)
              ? data.variants
              : [];

            const titleEl = document.getElementById("variantModalProductName");
            if (titleEl) titleEl.textContent = data.name || "Product";

            // Update summary cards
            const totalVariants = Array.isArray(window.__currentVariantData)
              ? window.__currentVariantData.length
              : 0;
            let totalStock = 0;

            if (Array.isArray(window.__currentVariantData)) {
              window.__currentVariantData.forEach((v) => {
                if (Array.isArray(v.sizeStocks)) {
                  v.sizeStocks.forEach((ss) => {
                    totalStock += ss.stock || 0;
                  });
                } else {
                  totalStock += v.stock || 0;
                }
              });
            }

            const totalVariantsEl =
              document.getElementById("totalVariantsCount");
            const totalStockEl = document.getElementById("totalStockCount");
            if (totalVariantsEl) totalVariantsEl.textContent = totalVariants;
            if (totalStockEl) totalStockEl.textContent = totalStock;

            const listEl = document.getElementById("variantStockList");
            listEl.innerHTML = "";

            if (
              Array.isArray(window.__currentVariantData) &&
              window.__currentVariantData.length
            ) {
              window.__currentVariantData.forEach((v, vi) => {
                const card = document.createElement("div");
                card.className = "variant-card";
                card.dataset.variantIndex = vi;

                // Create variant card header
                const header = document.createElement("div");
                header.className = "variant-card-header";

                // Photo
                const photoContainer = document.createElement("div");
                const photoSrc = v.photo || v.primary_image || "";
                if (
                  photoSrc &&
                  photoSrc !== "" &&
                  photoSrc !== "/static/image/banner.png"
                ) {
                  const photo = document.createElement("img");
                  photo.src = photoSrc;
                  photo.alt = "Variant photo";
                  photo.className = "variant-photo";
                  photo.onerror = function () {
                    // If image fails to load, show placeholder
                    this.style.display = "none";
                    const placeholder = document.createElement("div");
                    placeholder.className = "variant-photo-placeholder";
                    placeholder.innerHTML = '<i data-lucide="image"></i>';
                    photoContainer.appendChild(placeholder);
                    if (window.lucide) {
                      lucide.createIcons();
                    }
                  };
                  photoContainer.appendChild(photo);
                } else {
                  const placeholder = document.createElement("div");
                  placeholder.className = "variant-photo-placeholder";
                  placeholder.innerHTML = '<i data-lucide="image"></i>';
                  photoContainer.appendChild(placeholder);
                }

                // Variant info
                const info = document.createElement("div");
                info.className = "variant-info";

                const sku = document.createElement("h4");
                sku.className = "variant-sku";
                sku.textContent = v.sku || "Unnamed Variant";

                const colorInfo = document.createElement("div");
                colorInfo.className = "variant-color-info";

                if (v.color) {
                  const colorSwatch = document.createElement("div");
                  colorSwatch.className = "variant-color-swatch";
                  colorSwatch.style.backgroundColor = v.colorHex || "#000000";

                  const colorName = document.createElement("span");
                  colorName.className = "variant-color-name";
                  colorName.textContent = v.color;

                  colorInfo.appendChild(colorSwatch);
                  colorInfo.appendChild(colorName);
                }

                info.appendChild(sku);
                info.appendChild(colorInfo);

                // Actions
                const actions = document.createElement("div");
                actions.className = "variant-actions";

                const editSizesBtn = document.createElement("button");
                editSizesBtn.className = "btn-edit-sizes";
                editSizesBtn.innerHTML =
                  '<i data-lucide="edit-3"></i>Edit Sizes';
                editSizesBtn.title = "Edit sizes and stock levels";
                editSizesBtn.addEventListener("click", () =>
                  openSizeModalForVariant(vi)
                );

                actions.appendChild(editSizesBtn);

                header.appendChild(photoContainer);
                header.appendChild(info);
                header.appendChild(actions);

                // Sizes grid
                const sizesGrid = document.createElement("div");
                sizesGrid.className = "variant-sizes-grid";
                sizesGrid.id = `variant-sizes-${vi}`;

                // Populate sizes
                if (Array.isArray(v.sizeStocks) && v.sizeStocks.length) {
                  v.sizeStocks.forEach((ss, ssi) => {
                    const sizeCard = document.createElement("div");
                    sizeCard.className = "size-stock-card";

                    const sizeLabel = document.createElement("div");
                    sizeLabel.className = "size-label";
                    sizeLabel.textContent = ss.size || "N/A";

                    const stockValue = document.createElement("div");
                    stockValue.className = "stock-value";
                    const stock = ss.stock || 0;
                    stockValue.textContent = stock;

                    if (stock === 0) {
                      stockValue.classList.add("out");
                    } else if (stock < 5) {
                      stockValue.classList.add("low");
                    }

                    // Hidden input for form submission
                    const hiddenInput = document.createElement("input");
                    hiddenInput.type = "hidden";
                    hiddenInput.className = "variant-stock-input";
                    hiddenInput.dataset.variantIndex = vi;
                    hiddenInput.dataset.sizeIndex = ssi;
                    hiddenInput.value = stock;

                    sizeCard.appendChild(sizeLabel);
                    sizeCard.appendChild(stockValue);
                    sizeCard.appendChild(hiddenInput);
                    sizesGrid.appendChild(sizeCard);
                  });
                } else if (v.stock !== undefined) {
                  // Single stock variant
                  const sizeCard = document.createElement("div");
                  sizeCard.className = "size-stock-card";

                  const sizeLabel = document.createElement("div");
                  sizeLabel.className = "size-label";
                  sizeLabel.textContent = "Total Stock";

                  const stockValue = document.createElement("div");
                  stockValue.className = "stock-value";
                  const stock = v.stock || 0;
                  stockValue.textContent = stock;

                  if (stock === 0) {
                    stockValue.classList.add("out");
                  } else if (stock < 5) {
                    stockValue.classList.add("low");
                  }

                  // Hidden input for form submission
                  const hiddenInput = document.createElement("input");
                  hiddenInput.type = "hidden";
                  hiddenInput.className = "variant-stock-input";
                  hiddenInput.dataset.variantIndex = vi;
                  hiddenInput.value = stock;

                  sizeCard.appendChild(sizeLabel);
                  sizeCard.appendChild(stockValue);
                  sizeCard.appendChild(hiddenInput);
                  sizesGrid.appendChild(sizeCard);
                }

                card.appendChild(header);
                card.appendChild(sizesGrid);
                listEl.appendChild(card);
              });

              // Initialize Lucide icons for the new elements
              if (window.lucide) {
                lucide.createIcons();
              }
            }

            const variantModal = document.getElementById("variantStockModal");
            if (variantModal) variantModal.classList.add("active");
          })
          .catch((err) => {
            console.error("Failed to load variant details", err);
            alert("Failed to load variant details");
          });
        return;
      }

      // Edit product: open editable product detail modal
      if (editBtn) {
        const id = parseInt(editBtn.dataset.id);
        if (!id) return;
        fetch(`/seller/product/${id}/details`)
          .then((res) => {
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
          })
          .then((data) => {
            // Track which product is in the modal for saves
            window.__currentModalProductId = id;

            const imgEl = document.getElementById("modalProductImage");
            if (imgEl)
              imgEl.src = data.primary_image || "/static/image/banner.png";

            const nameInput = document.getElementById("modalProductName");
            if (nameInput) nameInput.value = data.name || "";

            const catInput = document.getElementById("modalProductCategory");
            if (catInput) catInput.value = data.category || "";

            const subcatInput = document.getElementById(
              "modalProductSubcategory"
            );
            if (subcatInput) subcatInput.value = data.subcategory || "";

            const priceInput = document.getElementById("modalProductPrice");
            if (priceInput)
              priceInput.value =
                data.price != null ? parseFloat(data.price) : "";

            const stockInput = document.getElementById("modalProductStock");
            if (stockInput)
              stockInput.value =
                data.total_stock != null ? data.total_stock : "";

            const descInput = document.getElementById(
              "modalProductDescription"
            );
            if (descInput) descInput.value = data.description || "";

            // Build editable sections: Basic Info, Description, Stocks
            const mainColumn = document.querySelector(".product-main-column");
            if (mainColumn) {
              // remove any previously injected sections
              [
                "modalSectionBasic",
                "modalSectionDescription",
                "modalSectionStocks",
              ].forEach((id) => {
                const el = document.getElementById(id);
                if (el) el.remove();
              });

              // BASIC INFO section (step1)
              const basic = document.createElement("div");
              basic.id = "modalSectionBasic";
              basic.className = "modal-section";
              basic.innerHTML = `
                <h3 class="section-title">Basic Information</h3>
                <div class="form-row">
                  <label for="modalProductName">Product Name</label>
                  <input type="text" id="modalProductName" class="modal-input" />
                </div>
                <div class="form-row form-row-split">
                  <div>
                    <label for="modalProductPrice">Price</label>
                    <input type="number" step="0.01" id="modalProductPrice" class="modal-input" />
                  </div>
                  <div>
                    <label for="modalDiscountPercentage">Discount</label>
                    <input type="number" step="0.01" id="modalDiscountPercentage" class="modal-input" />
                  </div>
                </div>
                <div class="form-row form-row-split">
                  <div>
                    <label for="modalDiscountType">Discount Type</label>
                    <select id="modalDiscountType" class="modal-input"><option value="">None</option><option value="percentage">Percentage</option><option value="fixed">Fixed</option></select>
                  </div>
                  <div>
                    <label for="modalVoucherType">Voucher Type</label>
                    <input type="text" id="modalVoucherType" class="modal-input" />
                  </div>
                </div>
                <div class="form-row form-row-split">
                  <div>
                    <label for="modalPrimaryImage">Primary Image (URL)</label>
                    <input type="text" id="modalPrimaryImage" class="modal-input" />
                  </div>
                  <div>
                    <label for="modalSecondaryImage">Secondary Image (URL)</label>
                    <input type="text" id="modalSecondaryImage" class="modal-input" />
                  </div>
                </div>
              `;

              // DESCRIPTION section (step2)
              const desc = document.createElement("div");
              desc.id = "modalSectionDescription";
              desc.className = "modal-section";
              desc.innerHTML = `
                <h3 class="section-title">Description & Attributes</h3>
                <div class="form-row">
                  <label for="modalProductDescription">Description</label>
                  <textarea id="modalProductDescription" class="modal-textarea" rows="4"></textarea>
                </div>
                <div class="form-row">
                  <label for="modalMaterials">Materials</label>
                  <textarea id="modalMaterials" class="modal-textarea" rows="2"></textarea>
                </div>
                <div class="form-row">
                  <label for="modalDetailsFit">Details / Fit</label>
                  <textarea id="modalDetailsFit" class="modal-textarea" rows="2"></textarea>
                </div>
                <div class="form-row form-row-split">
                  <div>
                    <label for="modalSizeGuides">Size Guides (comma separated)</label>
                    <input type="text" id="modalSizeGuides" class="modal-input" />
                  </div>
                  <div>
                    <label for="modalCertifications">Certifications (comma separated)</label>
                    <input type="text" id="modalCertifications" class="modal-input" />
                  </div>
                </div>
              `;

              // STOCKS / VARIANTS section (step3) - editable list
              const stocks = document.createElement("div");
              stocks.id = "modalSectionStocks";
              stocks.className = "modal-section";
              stocks.innerHTML = `
                <h3 class="section-title">Variants & Stocks</h3>
                <div id="modalProductVariants" class="variants-edit-list"></div>
              `;

              // append in order
              mainColumn.insertBefore(basic, mainColumn.firstChild);
              mainColumn.insertBefore(desc, basic.nextSibling);
              mainColumn.insertBefore(stocks, desc.nextSibling);

              // populate the fields we already set earlier
              document.getElementById("modalProductName").value =
                data.name || "";
              document.getElementById("modalProductPrice").value =
                data.price != null ? parseFloat(data.price) : "";
              document.getElementById("modalProductDescription").value =
                data.description || "";
              document.getElementById("modalMaterials").value =
                data.materials || "";
              document.getElementById("modalDetailsFit").value =
                data.details_fit || "";
              document.getElementById("modalPrimaryImage").value =
                data.primary_image || "";
              document.getElementById("modalSecondaryImage").value =
                data.secondary_image || "";
              document.getElementById("modalDiscountPercentage").value =
                data.discount_value != null
                  ? parseFloat(data.discount_value)
                  : "";
              document.getElementById("modalDiscountType").value =
                data.discount_type || "";
              document.getElementById("modalVoucherType").value =
                data.voucher_type || "";
              // attributes
              try {
                const attrs = data.attributes || {};
                document.getElementById("modalSizeGuides").value =
                  Array.isArray(attrs.size_guides)
                    ? attrs.size_guides.join(", ")
                    : attrs.size_guides || "";
                document.getElementById("modalCertifications").value =
                  Array.isArray(attrs.certifications)
                    ? attrs.certifications.join(", ")
                    : attrs.certifications || "";
                // subitems (checkbox style) not implemented here; kept in attributes
              } catch (e) {}

              // populate editable variants list
              const variantsContainer = document.getElementById(
                "modalProductVariants"
              );
              variantsContainer.innerHTML = "";
              const variants = Array.isArray(data.variants)
                ? data.variants
                : [];
              if (variants.length) {
                variants.forEach((v, vi) => {
                  const row = document.createElement("div");
                  row.className = "edit-variant-row";
                  row.dataset.variantIndex = vi;
                  row.innerHTML = `
                    <div class="variant-row-fields">
                      <input type="text" class="variant-input variant-sku" placeholder="SKU" value="${
                        v.sku || ""
                      }" />
                      <input type="text" class="variant-input variant-color" placeholder="Color" value="${
                        v.color || ""
                      }" />
                      <input type="text" class="variant-input variant-colorhex" placeholder="#hex" value="${
                        v.colorHex || v.colorHex || ""
                      }" />
                      <input type="text" class="variant-input variant-size" placeholder="Size" value="${
                        v.size || ""
                      }" />
                      <input type="number" class="variant-input variant-stock" placeholder="Stock" value="${
                        v.stock != null ? v.stock : 0
                      }" />
                    </div>
                  `;
                  variantsContainer.appendChild(row);
                });
              } else {
                variantsContainer.innerHTML =
                  '<div class="muted">No variants</div>';
              }
            }

            // Attributes
            const attrEl = document.getElementById("modalProductAttributes");
            try {
              attrEl.innerHTML = "";
              if (data.attributes) {
                const pre = document.createElement("pre");
                pre.textContent = JSON.stringify(data.attributes, null, 2);
                attrEl.appendChild(pre);
              } else {
                attrEl.textContent = "-";
              }
            } catch (err) {
              attrEl.textContent = "-";
            }

            if (productDetailModal) productDetailModal.classList.add("active");
          })
          .catch((err) => {
            console.error("Failed to load product details", err);
            alert("Failed to load product details");
          });
        return;
      }

      if (delBtn) {
        const id = parseInt(delBtn.dataset.id);
        const product = products.find((p) => p.id === id);

        console.log(`Delete button clicked for product ID: ${id}`);
        console.log("Product found in frontend array:", product);

        if (product) {
          showDeleteConfirmation(product);
        } else {
          console.error(`Product with ID ${id} not found in frontend array`);
          showNotification("Product not found", "error");
        }
      }
    });

  const selectAll = document.getElementById("selectAll");
  const bulkActions = document.getElementById("bulkActions");

  selectAll?.addEventListener("change", function () {
    document
      .querySelectorAll(".row-select")
      .forEach((cb) => (cb.checked = this.checked));
    bulkActions.style.display = getSelectedIds().length ? "" : "none";
  });

  document
    .getElementById("productTableBody")
    ?.addEventListener("change", function (e) {
      if (
        e.target &&
        e.target.classList &&
        e.target.classList.contains("row-select")
      ) {
        bulkActions.style.display = getSelectedIds().length ? "" : "none";
      }
    });

  document
    .getElementById("bulkRestock")
    ?.addEventListener("click", function () {
      const ids = getSelectedIds();
      products = products.map((p) =>
        ids.includes(p.id)
          ? Object.assign({}, p, { stock: (p.stock || 0) + 10 })
          : p
      );
      renderProducts(products);
      bulkActions.style.display = "none";
    });

  document
    .getElementById("bulkArchive")
    ?.addEventListener("click", function () {
      const ids = getSelectedIds();
      products = products.map((p) =>
        ids.includes(p.id) ? Object.assign({}, p, { status: "archived" }) : p
      );
      renderProducts(products);
      bulkActions.style.display = "none";
    });

  document.getElementById("bulkEdit")?.addEventListener("click", function () {
    alert("Bulk edit not implemented in frontend demo");
  });

  // Save changes from product detail modal to backend
  const saveProductBtn = document.getElementById("saveProductDetails");
  saveProductBtn?.addEventListener("click", function () {
    const id = window.__currentModalProductId;
    if (!id) return alert("No product selected");

    // Build payload including step1 (basic), step2 (description) and step3 (variants)
    const payload = {
      name: document.getElementById("modalProductName")?.value,
      category: document.getElementById("modalProductCategory")?.value,
      subcategory: document.getElementById("modalProductSubcategory")?.value,
      price:
        parseFloat(document.getElementById("modalProductPrice")?.value) || 0,
      total_stock:
        parseInt(document.getElementById("modalProductStock")?.value) || 0,
      description: document.getElementById("modalProductDescription")?.value,
      // Pricing extras
      discount_type:
        document.getElementById("modalDiscountType")?.value || null,
      discount_value: (function () {
        const v = document.getElementById("modalDiscountPercentage")?.value;
        return v !== undefined && v !== "" ? parseFloat(v) : null;
      })(),
      voucher_type: document.getElementById("modalVoucherType")?.value || null,
      primary_image:
        document.getElementById("modalPrimaryImage")?.value || null,
      secondary_image:
        document.getElementById("modalSecondaryImage")?.value || null,
      // Description / attributes
      materials: document.getElementById("modalMaterials")?.value || null,
      details_fit: document.getElementById("modalDetailsFit")?.value || null,
      attributes: {
        size_guides: (document.getElementById("modalSizeGuides")?.value || "")
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        certifications: (
          document.getElementById("modalCertifications")?.value || ""
        )
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      },
      // variants: collect from editable rows if present
      variants: (function () {
        const rows = Array.from(document.querySelectorAll(".edit-variant-row"));
        if (!rows.length) return undefined;
        return rows.map((r) => {
          return {
            sku: r.querySelector(".variant-sku")?.value || "",
            color: r.querySelector(".variant-color")?.value || "",
            colorHex: r.querySelector(".variant-colorhex")?.value || "",
            size: r.querySelector(".variant-size")?.value || "",
            stock:
              parseInt(r.querySelector(".variant-stock")?.value || "0") || 0,
          };
        });
      })(),
    };

    fetch(`/seller/product/${id}/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data && data.success && data.product) {
          // Replace product in local products array and re-render
          const updated = normalizeProduct(data.product);
          products = products.map((p) => (p.id === updated.id ? updated : p));
          renderProducts(products);
          if (productDetailModal) productDetailModal.classList.remove("active");
        } else {
          console.error("Failed to save product", data);
          alert("Failed to save product. Check console for details.");
        }
      })
      .catch((err) => {
        console.error("Error saving product", err);
        alert("Error saving product. See console.");
      });
  });

  // Save variant stocks handler
  const saveVariantBtn = document.getElementById("saveVariantStocks");
  saveVariantBtn?.addEventListener("click", function () {
    const id = window.__currentVariantProductId;
    if (!id) return alert("No product selected");

    const inputs = Array.from(
      document.querySelectorAll(".variant-stock-input")
    );
    const variants = JSON.parse(
      JSON.stringify(window.__currentVariantData || [])
    );

    inputs.forEach((inp) => {
      const vi = parseInt(inp.dataset.variantIndex);
      const si =
        inp.dataset.sizeIndex !== undefined
          ? parseInt(inp.dataset.sizeIndex)
          : null;
      const val = parseInt(inp.value) || 0;
      if (isNaN(vi) || !variants[vi]) return;
      if (
        si !== null &&
        Array.isArray(variants[vi].sizeStocks) &&
        variants[vi].sizeStocks[si]
      ) {
        variants[vi].sizeStocks[si].stock = val;
      } else {
        // top-level stock
        variants[vi].stock = val;
      }
    });

    // POST updated variants to backend
    fetch(`/seller/product/${id}/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ variants: variants }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data && data.success && data.product) {
          const updated = normalizeProduct(data.product);
          products = products.map((p) => (p.id === updated.id ? updated : p));
          renderProducts(products);
          const variantModal = document.getElementById("variantStockModal");
          if (variantModal) variantModal.classList.remove("active");
        } else {
          console.error("Failed to save variant stocks", data);
          alert("Failed to save variant stocks. See console.");
        }
      })
      .catch((err) => {
        console.error("Error saving variant stocks", err);
        alert("Error saving variant stocks. See console.");
      });
  });
});
// Size Selection Modal Functionality
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
      "EU 41",
      "EU 42",
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

let currentVariantIndex = null;

function openSizeModalForVariant(variantIndex) {
  currentVariantIndex = variantIndex;
  const variant = window.__currentVariantData[variantIndex];
  if (!variant) return;

  const sizeModal = document.getElementById("sizeSelectModal");
  const sizeOptionsContainer = document.getElementById("sizeOptionsContainer");
  const variantNameEl = document.getElementById("sizeModalVariantName");

  if (!sizeModal || !sizeOptionsContainer) return;

  // Set variant name in modal
  if (variantNameEl) {
    variantNameEl.textContent = `${variant.sku || "Variant"} ${
      variant.color ? " - " + variant.color : ""
    }`;
  }

  // Clear previous content
  sizeOptionsContainer.innerHTML = "";

  // Get existing size stocks
  const existingSizeStocks = variant.sizeStocks || [];
  const existingMap = {};
  existingSizeStocks.forEach((ss) => {
    existingMap[ss.size] = ss.stock || 0;
  });

  // Render size groups
  AVAILABLE_SIZE_GROUPS.forEach((group) => {
    const groupWrap = document.createElement("div");
    groupWrap.className = "size-group-container";

    const header = document.createElement("div");
    header.className = "size-group-header";

    const title = document.createElement("strong");
    title.textContent = group.name;

    const hint = document.createElement("span");
    hint.className = "size-group-hint";
    hint.textContent = group.hint ? `— ${group.hint}` : "";

    header.appendChild(title);
    header.appendChild(hint);

    const grid = document.createElement("div");
    grid.className = "size-group-grid";

    group.sizes.forEach((size) => {
      const wrapper = document.createElement("div");
      wrapper.className = "size-options-row";

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.className = "modal-size-checkbox";
      checkbox.dataset.size = size;
      checkbox.id = `modal_size_${size.replace(/\s+/g, "_")}_${variantIndex}`;

      if (existingMap[size] !== undefined) {
        checkbox.checked = true;
        wrapper.classList.add("size-selected");
      }

      const label = document.createElement("label");
      label.htmlFor = checkbox.id;
      label.className = "size-label-with-badge";
      label.textContent = size;

      const badge = document.createElement("span");
      badge.className = "size-category-badge";
      badge.textContent = group.name;
      label.appendChild(badge);

      const stockInput = document.createElement("input");
      stockInput.type = "number";
      stockInput.min = "0";
      stockInput.placeholder = "0";
      stockInput.className = "modal-size-stock";
      stockInput.dataset.for = checkbox.id;
      stockInput.value = existingMap[size] || "";
      stockInput.disabled = !checkbox.checked;

      // Handle checkbox changes
      checkbox.addEventListener("change", () => {
        stockInput.disabled = !checkbox.checked;
        wrapper.classList.toggle("size-selected", checkbox.checked);
        if (!checkbox.checked) {
          stockInput.value = "";
        }
      });

      wrapper.appendChild(checkbox);
      wrapper.appendChild(label);
      wrapper.appendChild(stockInput);
      grid.appendChild(wrapper);
    });

    groupWrap.appendChild(header);
    groupWrap.appendChild(grid);
    sizeOptionsContainer.appendChild(groupWrap);
  });

  // Show modal
  sizeModal.classList.add("active");

  // Initialize Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }
}

function closeSizeModal() {
  const sizeModal = document.getElementById("sizeSelectModal");
  if (sizeModal) {
    sizeModal.classList.remove("active");
  }
  currentVariantIndex = null;
}

function saveSizeModal() {
  if (currentVariantIndex === null) return;

  const sizeOptionsContainer = document.getElementById("sizeOptionsContainer");
  const checkedBoxes = Array.from(
    sizeOptionsContainer.querySelectorAll(".modal-size-checkbox:checked")
  );

  const newSizeStocks = [];
  checkedBoxes.forEach((checkbox) => {
    const size = checkbox.dataset.size;
    const stockInput = sizeOptionsContainer.querySelector(
      `.modal-size-stock[data-for="${checkbox.id}"]`
    );
    const stock = parseInt(stockInput?.value || "0", 10) || 0;

    newSizeStocks.push({ size, stock });
  });

  // Update the variant data
  if (window.__currentVariantData[currentVariantIndex]) {
    window.__currentVariantData[currentVariantIndex].sizeStocks = newSizeStocks;

    // Calculate total stock
    let totalStock = 0;
    newSizeStocks.forEach((ss) => (totalStock += ss.stock));
    window.__currentVariantData[currentVariantIndex].stock = totalStock;
  }

  // Update the UI
  updateVariantSizesDisplay(currentVariantIndex);
  updateSummaryCards();

  closeSizeModal();
}

function updateVariantSizesDisplay(variantIndex) {
  const sizesGrid = document.getElementById(`variant-sizes-${variantIndex}`);
  if (!sizesGrid) return;

  const variant = window.__currentVariantData[variantIndex];
  if (!variant) return;

  sizesGrid.innerHTML = "";

  if (Array.isArray(variant.sizeStocks) && variant.sizeStocks.length) {
    variant.sizeStocks.forEach((ss, ssi) => {
      const sizeCard = document.createElement("div");
      sizeCard.className = "size-stock-card";

      const sizeLabel = document.createElement("div");
      sizeLabel.className = "size-label";
      sizeLabel.textContent = ss.size || "N/A";

      const stockValue = document.createElement("div");
      stockValue.className = "stock-value";
      const stock = ss.stock || 0;
      stockValue.textContent = stock;

      if (stock === 0) {
        stockValue.classList.add("out");
      } else if (stock < 5) {
        stockValue.classList.add("low");
      }

      // Hidden input for form submission
      const hiddenInput = document.createElement("input");
      hiddenInput.type = "hidden";
      hiddenInput.className = "variant-stock-input";
      hiddenInput.dataset.variantIndex = variantIndex;
      hiddenInput.dataset.sizeIndex = ssi;
      hiddenInput.value = stock;

      sizeCard.appendChild(sizeLabel);
      sizeCard.appendChild(stockValue);
      sizeCard.appendChild(hiddenInput);
      sizesGrid.appendChild(sizeCard);
    });
  }
}

function updateSummaryCards() {
  if (!Array.isArray(window.__currentVariantData)) return;

  const totalVariants = window.__currentVariantData.length;
  let totalStock = 0;

  window.__currentVariantData.forEach((v) => {
    if (Array.isArray(v.sizeStocks)) {
      v.sizeStocks.forEach((ss) => {
        totalStock += ss.stock || 0;
      });
    } else {
      totalStock += v.stock || 0;
    }
  });

  const totalVariantsEl = document.getElementById("totalVariantsCount");
  const totalStockEl = document.getElementById("totalStockCount");
  if (totalVariantsEl) totalVariantsEl.textContent = totalVariants;
  if (totalStockEl) totalStockEl.textContent = totalStock;
}

// Size modal event listeners
const sizeModalSave = document.getElementById("sizeModalSave");
const sizeModalCancel = document.getElementById("sizeModalCancel");
const sizeModalClose = document.getElementById("sizeModalClose");

if (sizeModalSave) {
  sizeModalSave.addEventListener("click", saveSizeModal);
}

if (sizeModalCancel) {
  sizeModalCancel.addEventListener("click", closeSizeModal);
}

if (sizeModalClose) {
  sizeModalClose.addEventListener("click", closeSizeModal);
}

// Close modal when clicking outside
const sizeModal = document.getElementById("sizeSelectModal");
if (sizeModal) {
  sizeModal.addEventListener("click", (e) => {
    if (e.target === sizeModal) {
      closeSizeModal();
    }
  });
}

// Make functions globally available

// Delete confirmation functionality
let productToDelete = null;
let isDeletingProduct = false; // Prevent duplicate delete requests

function showDeleteConfirmation(product) {
  productToDelete = product;
  const modal = document.getElementById("deleteConfirmModal");
  const productNameEl = modal.querySelector(".product-name-to-delete");

  if (productNameEl) {
    productNameEl.textContent = product.name || "Unknown Product";
  }

  modal.classList.add("active");
}

function hideDeleteConfirmation() {
  const modal = document.getElementById("deleteConfirmModal");
  const confirmDelete = document.getElementById("confirmDelete");

  modal.classList.remove("active");
  productToDelete = null;

  // Reset deletion state and button
  isDeletingProduct = false;
  if (confirmDelete) {
    confirmDelete.disabled = false;
    confirmDelete.textContent = "Yes, Delete";
  }
}

async function deleteProduct(productId) {
  try {
    console.log(`Attempting to delete product ID: ${productId}`);

    const response = await fetch(`/seller/product/${productId}/delete`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log(`Delete response status: ${response.status}`);

    if (response.ok) {
      const result = await response.json();
      console.log("Delete response:", result);

      // Remove from frontend array immediately
      const productName =
        products.find((p) => p.id === productId)?.name || "Product";
      products = products.filter((p) => p.id !== productId);

      // Update UI immediately using existing filter function
      filterProducts();
      updateCounts();

      // Show success message
      showNotification("Product deleted", "success");

      return true;
    } else {
      let errorMessage = "Failed to delete product";
      try {
        const error = await response.json();
        errorMessage = error.message || errorMessage;
        console.log("Delete error response:", error);
      } catch (jsonError) {
        console.log("Could not parse error response as JSON");

        if (response.status === 404) {
          errorMessage = "Product not found or already deleted";
        } else if (response.status === 403) {
          errorMessage = "You don't have permission to delete this product";
        }
      }

      showNotification(errorMessage, "error");
      return false;
    }
  } catch (error) {
    console.error("Delete error:", error);
    // Network error notification removed as requested
    return false;
  }
}

function showNotification(message, type = "info") {
  // Create notification element
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    transition: all 0.3s ease;
  `;

  // Set background color based on type
  if (type === "success") {
    notification.style.backgroundColor = "#10b981";
  } else if (type === "error") {
    notification.style.backgroundColor = "#ef4444";
  } else {
    notification.style.backgroundColor = "#6b7280";
  }

  notification.textContent = message;
  document.body.appendChild(notification);

  // Auto remove after 3 seconds
  setTimeout(() => {
    notification.style.opacity = "0";
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 3000);
}

// Duplicate DOMContentLoaded listener removed to prevent double event handlers
window.openSizeModalForVariant = openSizeModalForVariant;
