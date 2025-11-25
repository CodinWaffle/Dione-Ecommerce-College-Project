document.addEventListener("DOMContentLoaded", () => {
  // Minimal, robust product management script
  if (window.lucide) lucide.createIcons();

  const productsRaw = window.__SELLER_PRODUCTS__ || [];
  let products = Array.isArray(productsRaw)
    ? JSON.parse(JSON.stringify(productsRaw))
    : [];

  const tbody = document.getElementById("productTableBody");

  // current tab filter: '', 'out-of-stock', 'active'
  let currentTabStatus = "";

  function updateCounts() {
    const countAllEl = document.getElementById("countAll");
    const countOutEl = document.getElementById("countOut");
    const countActiveEl = document.getElementById("countActive");
    if (countAllEl) countAllEl.textContent = `${products.length}`;
    if (countOutEl)
      countOutEl.textContent = `${
        products.filter((p) => computeStock(p) === 0).length
      }`;
    if (countActiveEl)
      countActiveEl.textContent = `${
        products.filter((p) => p.status === "active").length
      }`;
  }

  function applyTabFilter(status) {
    currentTabStatus = status || "";
    let list = products.slice();
    if (status === "out-of-stock") {
      list = list.filter((p) => computeStock(p) === 0);
    } else if (status === "active") {
      list = list.filter((p) => (p.status || "").toString() === "active");
    }
    renderProducts(list);
  }

  function getSelectedIds() {
    return Array.from(document.querySelectorAll(".row-select:checked")).map(
      (c) => parseInt(c.dataset.id, 10)
    );
  }

  // Product detail modal (edit fields except variants)
  function openProductDetailModal(productId, data) {
    const modal = document.getElementById("productDetailModal");
    if (!modal) return;
    document.getElementById("modalProductImage").src =
      data.primary_image || "/static/image/banner.png";
    document.getElementById("modalProductImage").dataset.pending = "";
    document.getElementById("modalProductName").value = data.name || "";
    document.getElementById("modalProductCategory").value = data.category || "";
    document.getElementById("modalProductSubcategory").value =
      data.subcategory || "";
    document.getElementById("modalProductPrice").value =
      data.price != null ? parseFloat(data.price) : "";
    document.getElementById("modalProductStock").value =
      data.total_stock != null ? data.total_stock : "";
    document.getElementById("modalProductDescription").value =
      data.description || "";

    // Variants: display read-only summary
    const variantsEl = document.getElementById("modalProductVariants");
    variantsEl.innerHTML = "";
    if (Array.isArray(data.variants) && data.variants.length) {
      data.variants.forEach((v, idx) => {
        const row = document.createElement("div");
        row.className = "modal-variant-row";
        row.style = "display:flex;gap:8px;align-items:center;margin-bottom:6px";
        const left = document.createElement("div");
        left.style = "flex:1";
        left.textContent = `${v.sku || "-"} / ${v.color || "-"} / ${
          Array.isArray(v.sizeStocks)
            ? v.sizeStocks.map((s) => s.size + ":" + s.stock).join(", ")
            : v.size || "-"
        }`;
        const right = document.createElement("div");
        right.style = "width:80px;text-align:right";
        right.textContent = `Stock: ${
          Array.isArray(v.sizeStocks)
            ? v.sizeStocks.reduce(
                (s, ss) => s + (parseInt(ss.stock || 0, 10) || 0),
                0
              )
            : v.stock || 0
        }`;
        row.appendChild(left);
        row.appendChild(right);
        variantsEl.appendChild(row);
      });
    } else {
      variantsEl.textContent = "No variants";
    }

    // Attributes as editable JSON textarea
    const attrEl = document.getElementById("modalProductAttributes");
    attrEl.innerHTML = "";
    try {
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

    // Image input preview
    const imageInput = document.getElementById("modalProductImageInput");
    if (imageInput) {
      imageInput.value = null;
      imageInput.onchange = function (ev) {
        const file = ev.target.files && ev.target.files[0];
        if (file && file.type && file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = function (e2) {
            document.getElementById("modalProductImage").src = e2.target.result;
            document.getElementById("modalProductImage").dataset.pending =
              e2.target.result;
          };
          reader.readAsDataURL(file);
        }
      };
    }

    // show modal
    modal.classList.add("active");
    document
      .getElementById("closeProductDetailModal")
      ?.addEventListener("click", () => modal.classList.remove("active"));
    document
      .getElementById("closeProductDetailModalFooter")
      ?.addEventListener("click", () => modal.classList.remove("active"));

    const saveBtn = document.getElementById("saveProductDetails");
    if (saveBtn) {
      const newSave = saveBtn.cloneNode(true);
      saveBtn.parentNode.replaceChild(newSave, saveBtn);
      newSave.addEventListener("click", async () => {
        const payload = {};
        payload.name = document.getElementById("modalProductName").value;
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
          parseFloat(document.getElementById("modalProductPrice").value) || 0;
        payload.total_stock =
          parseInt(
            document.getElementById("modalProductStock").value || "0",
            10
          ) || 0;
        try {
          const attrText =
            document.getElementById("modalProductAttributesInput").value || "";
          payload.attributes = attrText ? JSON.parse(attrText) : {};
        } catch (err) {
          alert("Attributes JSON is invalid");
          return;
        }
        const pending =
          document.getElementById("modalProductImage").dataset.pending;
        if (pending) payload.primary_image = pending;
        // Do NOT include variants (user asked variants are not editable here)
        try {
          const res = await fetch(`/seller/product/${productId}/update`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          const resp = await res.json();
          if (resp && resp.success) {
            const idx = products.findIndex((p) => p.id === productId);
            if (idx !== -1)
              products[idx] = Object.assign({}, products[idx], resp.product);
            else products.unshift(resp.product);
            applyTabFilter(currentTabStatus);
            modal.classList.remove("active");
            alert("Product updated successfully");
          } else {
            alert("Failed to save product");
          }
        } catch (err) {
          console.error("Save failed", err);
          alert("Failed to save product");
        }
      });
    }
  }

  function formatPrice(p) {
    return (parseFloat(p || 0) || 0).toFixed(2);
  }

  function computeStock(product) {
    if (product.total_stock != null) return product.total_stock;
    if (product.variants && Array.isArray(product.variants)) {
      return product.variants.reduce((acc, v) => {
        if (Array.isArray(v.sizeStocks))
          return (
            acc +
            v.sizeStocks.reduce(
              (s, ss) => s + (parseInt(ss.stock || 0, 10) || 0),
              0
            )
          );
        return acc + (parseInt(v.stock || 0, 10) || 0);
      }, 0);
    }
    return product.stock || 0;
  }

  function renderProducts(list) {
    if (!tbody) return;
    tbody.innerHTML = "";
    list.forEach((product) => {
      const tr = document.createElement("tr");
      tr.dataset.id = product.id;
      const stockVal = computeStock(product);
      let status = product.status || "";
      let statusClass = "active";
      if (stockVal === 0) {
        status = "Not Active";
        statusClass = "inactive";
      } else if (stockVal <= 10) {
        status = "Low Stocks";
        statusClass = "low-stocks";
      }

      tr.innerHTML = `
        <td><input type="checkbox" class="row-select" data-id="${
          product.id
        }"></td>
        <td>
          <div class="product-info">
            <img src="${
              product.primary_image || "/static/image/banner.png"
            }" class="product-image" />
            <span class="product-name">${(product.name || "").replace(
              /</g,
              "&lt;"
            )}</span>
          </div>
        </td>
        <td>${product.category || ""}</td>
        <td>${product.subcategory || "—"}</td>
        <td>$${formatPrice(product.price)}</td>
        <td><span class="stock-value">${stockVal}</span></td>
        <td><span class="status-badge status-${statusClass}">${status}</span></td>
        <td>
          <div class="action-buttons">
            <button class="btn-icon open-variants" data-id="${
              product.id
            }" title="Manage variant stocks"><i data-lucide="layers"></i></button>
            <button class="btn-icon edit-product" data-id="${
              product.id
            }" title="Edit product"><i data-lucide="edit"></i></button>
            <button class="btn-icon delete-product" data-id="${
              product.id
            }" title="Delete product"><i data-lucide="trash-2"></i></button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
    if (window.lucide) lucide.createIcons();
    updateCounts();
  }

  // If no preloaded array, attempt to parse DOM-rendered rows
  if (
    (!Array.isArray(products) || products.length === 0) &&
    document.querySelectorAll("#productTableBody tr").length
  ) {
    const rows = Array.from(document.querySelectorAll("#productTableBody tr"));
    products = rows
      .map((r) => {
        const id = parseInt(r.dataset.id, 10) || null;
        const name = r.querySelector(".product-name")?.textContent.trim() || "";
        const img =
          r.querySelector(".product-image")?.src || "/static/image/banner.png";
        const tds = r.querySelectorAll("td");
        const category = tds[2]?.textContent.trim() || "";
        const subcategory = tds[3]?.textContent.trim() || "";
        const price =
          parseFloat((tds[4]?.textContent || "").replace(/[^0-9.\-]/g, "")) ||
          0;
        const stock = parseInt(tds[5]?.textContent.trim() || "0", 10) || 0;
        return {
          id,
          name,
          primary_image: img,
          category,
          subcategory,
          price,
          total_stock: stock,
        };
      })
      .filter((p) => p.id !== null);
  }

  // initial render respects current tab (default: all)
  applyTabFilter(currentTabStatus);

  // Tab click handlers (All / Out of stock / Active)
  const tabAll = document.getElementById("tabAll");
  const tabOut = document.getElementById("tabOut");
  const tabActive = document.getElementById("tabActive");
  function setActiveTab(el) {
    document.querySelectorAll(".seller-nav-tabs .tab").forEach((t) => {
      t.classList.remove("active");
      t.setAttribute("aria-selected", "false");
    });
    if (el) {
      el.classList.add("active");
      el.setAttribute("aria-selected", "true");
    }
  }
  tabAll?.addEventListener("click", () => {
    setActiveTab(tabAll);
    applyTabFilter("");
  });
  tabOut?.addEventListener("click", () => {
    setActiveTab(tabOut);
    applyTabFilter("out-of-stock");
  });
  tabActive?.addEventListener("click", () => {
    setActiveTab(tabActive);
    applyTabFilter("active");
  });

  // Delegated handlers
  document
    .getElementById("productTableBody")
    ?.addEventListener("click", async (e) => {
      const openBtn = e.target.closest(".open-variants");
      if (openBtn) {
        const id = parseInt(openBtn.dataset.id, 10);
        try {
          const res = await fetch(`/seller/product/${id}/details`);
          if (!res.ok) throw new Error("Fetch failed");
          const data = await res.json();
          openVariantModal(id, data);
        } catch (err) {
          console.error("Failed to load product variants", err);
          alert("Failed to load product variants");
        }
        return;
      }

      const editBtn = e.target.closest(".edit-product");
      if (editBtn) {
        const id = parseInt(editBtn.dataset.id, 10);
        // open product detail modal with editable fields (variants read-only)
        try {
          const res = await fetch(`/seller/product/${id}/details`);
          if (!res.ok) throw new Error("Failed to fetch product");
          const data = await res.json();
          openProductDetailModal(id, data);
        } catch (err) {
          console.error("Failed to load product details", err);
          alert("Failed to load product details");
        }
        return;
      }

      const delBtn = e.target.closest(".delete-product");
      if (delBtn) {
        const id = parseInt(delBtn.dataset.id, 10);
        products = products.filter((p) => p.id !== id);
        applyTabFilter(currentTabStatus);
        return;
      }
    });

  // Bulk controls
  const selectAll = document.getElementById("selectAll");
  const bulkActions = document.getElementById("bulkActions");
  selectAll?.addEventListener("change", function () {
    document
      .querySelectorAll(".row-select")
      .forEach((cb) => (cb.checked = this.checked));
    if (bulkActions)
      bulkActions.style.display = getSelectedIds().length ? "" : "none";
  });
  document
    .getElementById("productTableBody")
    ?.addEventListener("change", (e) => {
      if (e.target?.classList?.contains("row-select"))
        if (bulkActions)
          bulkActions.style.display = getSelectedIds().length ? "" : "none";
    });

  document.getElementById("bulkRestock")?.addEventListener("click", () => {
    const ids = getSelectedIds();
    products = products.map((p) =>
      ids.includes(p.id)
        ? Object.assign({}, p, { total_stock: (computeStock(p) || 0) + 10 })
        : p
    );
    applyTabFilter(currentTabStatus);
    if (bulkActions) bulkActions.style.display = "none";
  });
  document.getElementById("bulkArchive")?.addEventListener("click", () => {
    const ids = getSelectedIds();
    products = products.map((p) =>
      ids.includes(p.id) ? Object.assign({}, p, { status: "archived" }) : p
    );
    applyTabFilter(currentTabStatus);
    if (bulkActions) bulkActions.style.display = "none";
  });

  // Add Product button handler
  document.getElementById("addProductBtn")?.addEventListener("click", () => {
    // Redirect to the add product page
    window.location.href = "/seller/add_product";
  });

  // Variant modal helper
  function openVariantModal(productId, productData) {
    const modal = document.getElementById("variantStockModal");
    const nameEl = document.getElementById("variantModalProductName");
    const listEl = document.getElementById("variantStockList");
    if (!modal || !listEl || !nameEl) return;
    nameEl.textContent = productData.name || "-";
    listEl.innerHTML = "";
    const variants = Array.isArray(productData.variants)
      ? productData.variants
      : [];
    if (!variants.length) {
      const msg = document.createElement("div");
      msg.textContent = "No variants available for this product.";
      listEl.appendChild(msg);
    } else {
      variants.forEach((v, idx) => {
        const container = document.createElement("div");
        container.className = "variant-edit-row";
        container.dataset.idx = idx;
        const left = document.createElement("div");
        left.style = "display:flex;gap:8px;align-items:center;";
        const sku = document.createElement("input");
        sku.className = "variant-sku";
        sku.placeholder = "SKU";
        sku.value = v.sku || "";
        const color = document.createElement("input");
        color.className = "variant-color";
        color.placeholder = "Color";
        color.value = v.color || "";
        left.appendChild(sku);
        left.appendChild(color);
        container.appendChild(left);
        // sizes area
        const sizesWrap = document.createElement("div");
        sizesWrap.className = "variant-size-wrap";
        if (Array.isArray(v.sizeStocks) && v.sizeStocks.length) {
          v.sizeStocks.forEach((ss, sidx) => {
            const row = document.createElement("div");
            row.className = "size-edit-row";
            row.style =
              "display:flex;gap:6px;margin-top:6px;align-items:center;";
            const sizeInput = document.createElement("input");
            sizeInput.className = "size-input";
            sizeInput.value = ss.size;
            sizeInput.placeholder = "Size";
            const stockInput = document.createElement("input");
            stockInput.className = "size-stock-input";
            stockInput.type = "number";
            stockInput.min = 0;
            stockInput.value = ss.stock || 0;
            stockInput.style.width = "80px";
            row.appendChild(sizeInput);
            row.appendChild(stockInput);
            sizesWrap.appendChild(row);
          });
        } else {
          const row = document.createElement("div");
          row.className = "size-edit-row";
          row.style = "display:flex;gap:6px;margin-top:6px;align-items:center;";
          const sizeInput = document.createElement("input");
          sizeInput.className = "size-input";
          sizeInput.placeholder = "Size";
          sizeInput.value = v.size || "";
          const stockInput = document.createElement("input");
          stockInput.className = "size-stock-input";
          stockInput.type = "number";
          stockInput.min = 0;
          stockInput.value = v.stock || 0;
          stockInput.style.width = "80px";
          row.appendChild(sizeInput);
          row.appendChild(stockInput);
          sizesWrap.appendChild(row);
        }
        container.appendChild(sizesWrap);
        listEl.appendChild(container);
      });
    }
    modal.classList.add("active");
    document
      .getElementById("closeVariantStockModal")
      ?.addEventListener("click", () => modal.classList.remove("active"));
    document
      .getElementById("closeVariantStockModalFooter")
      ?.addEventListener("click", () => modal.classList.remove("active"));

    const saveBtn = document.getElementById("saveVariantStocks");
    if (saveBtn) {
      const newSave = saveBtn.cloneNode(true);
      saveBtn.parentNode.replaceChild(newSave, saveBtn);
      newSave.addEventListener("click", async () => {
        // collect updated variants
        const rows = listEl.querySelectorAll(".variant-edit-row");
        const updated = [];
        let total = 0;
        rows.forEach((r) => {
          const sku = r.querySelector(".variant-sku")?.value || "";
          const color = r.querySelector(".variant-color")?.value || "";
          const sizeRows = Array.from(r.querySelectorAll(".size-edit-row"));
          if (sizeRows.length > 1) {
            const sizeStocks = sizeRows.map((sr) => ({
              size: sr.querySelector(".size-input")?.value || "",
              stock:
                parseInt(
                  sr.querySelector(".size-stock-input")?.value || "0",
                  10
                ) || 0,
            }));
            const vTotal = sizeStocks.reduce(
              (s, ss) => s + (parseInt(ss.stock || 0, 10) || 0),
              0
            );
            total += vTotal;
            updated.push({ sku, color, sizeStocks });
          } else {
            const s = sizeRows[0];
            const sizeVal = s.querySelector(".size-input")?.value || "";
            const stockVal =
              parseInt(
                s.querySelector(".size-stock-input")?.value || "0",
                10
              ) || 0;
            total += stockVal;
            updated.push({ sku, color, size: sizeVal, stock: stockVal });
          }
        });
        const payload = { variants: updated, total_stock: total };
        try {
          const res = await fetch(`/seller/product/${productId}/update`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          const resp = await res.json();
          if (resp && resp.success) {
            const idx = products.findIndex((p) => p.id === productId);
            if (idx !== -1)
              products[idx] = Object.assign({}, products[idx], resp.product);
            applyTabFilter(currentTabStatus);
            modal.classList.remove("active");
            alert("Variant stocks updated");
          } else {
            alert("Failed to update variant stocks");
          }
        } catch (err) {
          console.error("Update failed", err);
          alert("Failed to update variant stocks");
        }
      });
    }
  }
});
