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
  const closeModalBtns = document.querySelectorAll(".close-modal");
  const productForm = document.getElementById("productForm");
  const imageUpload = document.getElementById("imageUpload");
  const imagePreview = document.getElementById("imagePreview");
  const searchInput = document.querySelector(".search-box input");
  const categoryFilter = document.getElementById("filterCategory");
  const statusFilter = document.getElementById("filterStatus");

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
  let products = Array.isArray(preloaded)
    ? JSON.parse(JSON.stringify(preloaded))
    : [];

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

  // Tab elements
  const tabAll = document.getElementById("tabAll");
  const tabOut = document.getElementById("tabOut");
  const tabActive = document.getElementById("tabActive");

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
      (p) =>
        (p.total_stock !== undefined ? p.total_stock === 0 : p.stock === 0) ||
        p.status === "out-of-stock"
    ).length;
    const active = products.filter((p) => p.status === "active").length;
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
    const searchTerm = searchInput.value.toLowerCase();
    const categoryValue = categoryFilter.value;
    const statusValue = statusFilter.value;

    const filteredProducts = products.filter((product) => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm);
      const matchesCategory =
        !categoryValue || product.category === categoryValue;
      let matchesStatus = false;
      if (!statusValue) {
        matchesStatus = true;
      } else if (statusValue === "out-of-stock") {
        // treat out-of-stock tab as products with zero stock OR explicit out-of-stock status
        const stockVal =
          product.total_stock !== undefined
            ? product.total_stock
            : product.stock;
        matchesStatus = stockVal === 0 || product.status === "out-of-stock";
      } else {
        matchesStatus = product.status === statusValue;
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
                <td><input type="checkbox" class="row-select" data-id="${
                  product.id
                }"></td>
                <td>
                    <div class="product-info">
                        <img src="${
                          product.primary_image ||
                          product.image ||
                          "/static/image/banner.png"
                        }" alt="${product.name}" class="product-image">
                        <span class="product-name">${product.name}</span>
                    </div>
                </td>
                <td>${product.category}</td>
                <td>${product.subcategory || "—"}</td>
                <td>$${
                  product.price ? parseFloat(product.price).toFixed(2) : "0.00"
                }</td>
                <td>
                  <div style="display:flex;align-items:center;gap:8px">
                    <input type="number" min="0" class="stock-edit" data-id="${
                      product.id
                    }" value="${
        product.total_stock !== undefined
          ? product.total_stock
          : product.stock !== undefined
          ? product.stock
          : 0
      }" style="width:80px;padding:6px;border-radius:6px;border:1px solid #e5e7eb;" />
                    <button class="btn-icon open-variants" data-id="${
                      product.id
                    }" title="Edit variants">
                      <i data-lucide="layers"></i>
                    </button>
                  </div>
                </td>
                <td><span class="status-badge status-${product.status}">${
        product.status
      }</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon edit-product" data-id="${
                          product.id
                        }">
                            <i data-lucide="edit"></i>
                        </button>
                        <button class="btn-icon delete-product" data-id="${
                          product.id
                        }">
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
  }

  // If there were no preloaded products, parse server-rendered rows and use those
  if (!Array.isArray(products) || products.length === 0) {
    const fromDom = parseServerRenderedRows();
    if (fromDom && fromDom.length > 0) products = fromDom;
  }
  renderProducts(products);

  // Handle inline stock edits via delegation
  document
    .getElementById("productTableBody")
    ?.addEventListener("change", function (e) {
      const input = e.target;
      if (input && input.classList && input.classList.contains("stock-edit")) {
        const id = parseInt(input.dataset.id);
        const newVal = parseInt(input.value || "0", 10) || 0;
        const idx = products.findIndex((p) => p.id === id);
        if (idx !== -1) {
          // Update total_stock or stock depending on schema
          if (products[idx].hasOwnProperty("total_stock")) {
            products[idx].total_stock = newVal;
          } else {
            products[idx].stock = newVal;
          }
          updateCounts();
        }
      }
    });

  // Open variant-stock modal when open-variants button clicked
  document
    .getElementById("productTableBody")
    ?.addEventListener("click", function (e) {
      const btn = e.target.closest(".open-variants");
      if (btn) {
        const id = parseInt(btn.dataset.id);
        if (!id) return;
        // fetch product details then populate modal
        fetch(`/seller/product/${id}/details`)
          .then((res) => {
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
          })
          .then((data) => {
            const modal = document.getElementById("variantStockModal");
            const nameEl = document.getElementById("variantModalProductName");
            const listEl = document.getElementById("variantStockList");
            listEl.innerHTML = "";
            nameEl.textContent = data.name || "-";

            const variants = Array.isArray(data.variants) ? data.variants : [];
            if (variants.length === 0) {
              const msg = document.createElement("div");
              msg.textContent = "No variants available for this product.";
              listEl.appendChild(msg);
            } else {
              variants.forEach((v, idx) => {
                const row = document.createElement("div");
                row.className = "variant-edit-row";
                row.style = "display:flex;gap:8px;align-items:center;";
                row.innerHTML = `
                  <input data-idx="${idx}" class="variant-sku" placeholder="SKU" value="${
                  v.sku || ""
                }" />
                  <input data-idx="${idx}" class="variant-color" placeholder="Color" value="${
                  v.color || ""
                }" />
                  <input data-idx="${idx}" class="variant-size" placeholder="Size" value="${
                  v.size || ""
                }" />
                  <input data-idx="${idx}" type="number" min="0" class="variant-stock" placeholder="Stock" value="${
                  v.stock != null ? v.stock : 0
                }" style="width:80px" />
                `;
                listEl.appendChild(row);
              });
            }

            // show modal
            if (modal) modal.classList.add("active");

            // attach close handlers
            document
              .getElementById("closeVariantStockModal")
              ?.addEventListener("click", () =>
                modal.classList.remove("active")
              );
            document
              .getElementById("closeVariantStockModalFooter")
              ?.addEventListener("click", () =>
                modal.classList.remove("active")
              );

            // Save stocks handler
            const saveBtn = document.getElementById("saveVariantStocks");
            if (saveBtn) {
              // remove previous click handlers to avoid duplicates
              saveBtn.replaceWith(saveBtn.cloneNode(true));
            }
            const freshSave = document.getElementById("saveVariantStocks");
            freshSave.addEventListener("click", function () {
              // collect updated variants
              const rows = listEl.querySelectorAll(".variant-edit-row");
              const updated = [];
              let total = 0;
              rows.forEach((r) => {
                const sku = r.querySelector(".variant-sku")?.value || "";
                const color = r.querySelector(".variant-color")?.value || "";
                const size = r.querySelector(".variant-size")?.value || "";
                const stock =
                  parseInt(
                    r.querySelector(".variant-stock")?.value || "0",
                    10
                  ) || 0;
                updated.push({ sku, color, size, stock });
                total += stock;
              });

              const payload = { variants: updated, total_stock: total };

              fetch(`/seller/product/${id}/update`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
              })
                .then((res) => res.json())
                .then((resp) => {
                  if (resp && resp.success) {
                    // update local products array
                    const idx = products.findIndex((p) => p.id === id);
                    if (idx !== -1) {
                      products[idx] = Object.assign(
                        {},
                        products[idx],
                        resp.product
                      );
                    }
                    renderProducts(products);
                    document
                      .getElementById("variantStockModal")
                      ?.classList.remove("active");
                    alert("Variant stocks updated");
                  } else {
                    alert("Failed to update variant stocks");
                  }
                })
                .catch((err) => {
                  console.error("Update failed", err);
                  alert("Failed to update variant stocks");
                });
            });
          })
          .catch((err) => {
            console.error("Failed to load product variants", err);
            alert("Failed to load product variants");
          });
      }
    });

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
  } else {
    console.error("[v0] CRITICAL: addProductBtn not found - button won't work");
  }

  closeModalBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (productModal) {
        productModal.classList.remove("active");
      }
    });
  });

  // Close product detail modal
  if (closeProductDetailBtn) {
    closeProductDetailBtn.addEventListener("click", () => {
      if (productDetailModal) productDetailModal.classList.remove("active");
    });
  }

  if (productDetailModal) {
    productDetailModal.addEventListener("click", (e) => {
      if (e.target === productDetailModal)
        productDetailModal.classList.remove("active");
    });
  }

  // Close modal when clicking outside
  if (productModal) {
    productModal.addEventListener("click", (e) => {
      if (e.target === productModal) {
        productModal.classList.remove("active");
      }
    });
  }

  if (productForm) {
    productForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const product = {
        id: Date.now(),
        name: document.getElementById("productName").value,
        category: document.getElementById("productCategory").value,
        price: parseFloat(document.getElementById("productPrice").value) || 0,
        stock: parseInt(document.getElementById("productStock").value) || 0,
        status: "active",
        image:
          imagePreview.querySelector("img")?.src || "/static/image/banner.png",
      };
      products.unshift(product);
      renderProducts(products);
      if (productModal) {
        productModal.classList.remove("active");
      }
    });
  }

  if (imageUpload) {
    imageUpload.addEventListener("click", () => {
      const input = imageUpload.querySelector('input[type="file"]');
      if (input) input.click();
    });

    const fileInput = imageUpload.querySelector('input[type="file"]');
    if (fileInput) {
      fileInput.addEventListener("change", (e) => {
        const files = e.target.files;
        handleImageFiles(files);
      });
    }
  }

  if (imageUpload) {
    imageUpload.addEventListener("dragover", (e) => {
      e.preventDefault();
      imageUpload.classList.add("dragover");
    });

    imageUpload.addEventListener("dragleave", () => {
      imageUpload.classList.remove("dragover");
    });

    imageUpload.addEventListener("drop", (e) => {
      e.preventDefault();
      imageUpload.classList.remove("dragover");
      const files = e.dataTransfer.files;
      handleImageFiles(files);
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", filterProducts);
  }
  if (categoryFilter) {
    categoryFilter.addEventListener("change", filterProducts);
  }
  if (statusFilter) {
    statusFilter.addEventListener("change", filterProducts);
  }

  document
    .getElementById("importProductsBtn")
    ?.addEventListener("click", function () {
      alert("Import not implemented.");
    });
  document
    .getElementById("exportProductsBtn")
    ?.addEventListener("click", function () {
      alert("Export not implemented.");
    });

  document
    .getElementById("productTableBody")
    ?.addEventListener("click", function (e) {
      const viewBtn = e.target.closest(".view-product");
      const editBtn = e.target.closest(".edit-product");
      const delBtn = e.target.closest(".delete-product");
      if (viewBtn) {
        const id = parseInt(viewBtn.dataset.id);
        if (!id) return;
        fetch(`/seller/product/${id}/details`)
          .then((res) => {
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
          })
          .then((data) => {
            // Populate editable modal fields
            document.getElementById("modalProductImage").src =
              data.primary_image || "/static/image/banner.png";
            document.getElementById("modalProductName").value = data.name || "";
            document.getElementById("modalProductCategory").value =
              data.category || "";
            document.getElementById("modalProductSubcategory").value =
              data.subcategory || "";
            document.getElementById("modalProductPrice").value =
              data.price != null ? parseFloat(data.price) : "";
            document.getElementById("modalProductStock").value =
              data.total_stock != null
                ? data.total_stock
                : data.total_stock === 0
                ? 0
                : "";
            document.getElementById("modalProductDescription").value =
              data.description || "";

            // Variants - render editable rows
            const variantsEl = document.getElementById("modalProductVariants");
            variantsEl.innerHTML = "";
            if (Array.isArray(data.variants) && data.variants.length) {
              data.variants.forEach((v, idx) => {
                const row = document.createElement("div");
                row.className = "modal-variant-row";
                row.style =
                  "display:flex;gap:8px;align-items:center;margin-bottom:6px";
                row.innerHTML = `
                  <input data-idx="${idx}" class="variant-sku" placeholder="SKU" value="${
                  v.sku || ""
                }" />
                  <input data-idx="${idx}" class="variant-color" placeholder="Color" value="${
                  v.color || ""
                }" />
                  <input data-idx="${idx}" class="variant-size" placeholder="Size" value="${
                  v.size || ""
                }" />
                  <input data-idx="${idx}" type="number" min="0" class="variant-stock" placeholder="Stock" value="${
                  v.stock != null ? v.stock : 0
                }" style="width:80px" />
                `;
                variantsEl.appendChild(row);
              });
            } else {
              variantsEl.textContent = "No variants";
            }

            // Attributes - render JSON editor (simple textarea)
            const attrEl = document.getElementById("modalProductAttributes");
            try {
              attrEl.innerHTML = "";
              const ta = document.createElement("textarea");
              ta.id = "modalProductAttributesInput";
              ta.rows = 6;
              ta.className = "modal-textarea";
              ta.value = data.attributes
                ? JSON.stringify(data.attributes, null, 2)
                : "";
              attrEl.appendChild(ta);
            } catch (err) {
              attrEl.textContent = "-";
            }

            // Attach image input handler to preview selected file
            const imageInput = document.getElementById(
              "modalProductImageInput"
            );
            imageInput.value = null;
            imageInput.onchange = function (ev) {
              const file = ev.target.files && ev.target.files[0];
              if (file && file.type && file.type.startsWith("image/")) {
                const reader = new FileReader();
                reader.onload = function (e2) {
                  document.getElementById("modalProductImage").src =
                    e2.target.result;
                  // store data URL temporarily on the element for save
                  document.getElementById("modalProductImage").dataset.pending =
                    e2.target.result;
                };
                reader.readAsDataURL(file);
              }
            };

            // Show modal
            if (productDetailModal) productDetailModal.classList.add("active");

            // wire close footer button
            const closeFooter = document.getElementById(
              "closeProductDetailModalFooter"
            );
            if (closeFooter)
              closeFooter.onclick = () =>
                productDetailModal.classList.remove("active");

            // wire save button
            const saveBtn = document.getElementById("saveProductDetails");
            if (saveBtn) {
              saveBtn.onclick = function () {
                // collect data
                const payload = {};
                payload.name =
                  document.getElementById("modalProductName").value;
                payload.description = document.getElementById(
                  "modalProductDescription"
                ).value;
                payload.category = document.getElementById(
                  "modalProductCategory"
                ).value;
                payload.subcategory = document.getElementById(
                  "modalProductSubcategory"
                ).value;
                payload.price =
                  parseFloat(
                    document.getElementById("modalProductPrice").value
                  ) || 0;
                payload.total_stock = parseInt(
                  document.getElementById("modalProductStock").value || "0",
                  10
                );
                // variants
                const vs = [];
                const rows = variantsEl.querySelectorAll(".modal-variant-row");
                rows.forEach((r) => {
                  const sku = r.querySelector(".variant-sku")?.value || "";
                  const color = r.querySelector(".variant-color")?.value || "";
                  const size = r.querySelector(".variant-size")?.value || "";
                  const stock =
                    parseInt(
                      r.querySelector(".variant-stock")?.value || "0",
                      10
                    ) || 0;
                  vs.push({ sku, color, size, stock });
                });
                payload.variants = vs;
                // attributes
                try {
                  const attrText =
                    document.getElementById("modalProductAttributesInput")
                      .value || "";
                  payload.attributes = attrText ? JSON.parse(attrText) : {};
                } catch (err) {
                  alert("Attributes JSON is invalid");
                  return;
                }
                // primary_image (use pending data URL if present)
                const pending =
                  document.getElementById("modalProductImage").dataset.pending;
                if (pending) payload.primary_image = pending;

                fetch(`/seller/product/${id}/update`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify(payload),
                })
                  .then((res) => res.json())
                  .then((resp) => {
                    if (resp && resp.success) {
                      // update local products array and re-render
                      const idx = products.findIndex((p) => p.id === id);
                      if (idx !== -1) {
                        products[idx] = Object.assign(
                          {},
                          products[idx],
                          resp.product
                        );
                      } else {
                        products.unshift(resp.product);
                      }
                      renderProducts(products);
                      productDetailModal.classList.remove("active");
                      alert("Product updated successfully");
                    } else {
                      alert("Failed to save product");
                    }
                  })
                  .catch((err) => {
                    console.error("Save failed", err);
                    alert("Failed to save product");
                  });
              };
            }
          })
          .catch((err) => {
            console.error("Failed to load product details", err);
            alert("Failed to load product details");
          });
        return;
      }
      if (editBtn) {
        const id = parseInt(editBtn.dataset.id);
        const p = products.find((x) => x.id === id);
        if (p) {
          document.getElementById("modalTitle").textContent = "Edit Product";
          document.getElementById("productName").value = p.name;
          document.getElementById("productPrice").value = p.price;
          document.getElementById("productStock").value = p.stock;
          document.getElementById("productCategory").value = p.category;
          imagePreview.innerHTML = `<img src="${p.image}" class="preview-image">`;
          productModal.classList.add("active");
        }
      }
      if (delBtn) {
        const id = parseInt(delBtn.dataset.id);
        products = products.filter((x) => x.id !== id);
        renderProducts(products);
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
          ? Object.assign(
              {},
              p,
              p.total_stock !== undefined
                ? { total_stock: (p.total_stock || 0) + 10 }
                : { stock: (p.stock || 0) + 10 }
            )
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
});
