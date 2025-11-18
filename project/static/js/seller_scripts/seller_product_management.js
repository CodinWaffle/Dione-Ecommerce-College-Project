document.addEventListener("DOMContentLoaded", function () {
  // Initialize Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Load and render products from localStorage
  function loadProducts() {
    const products = JSON.parse(localStorage.getItem("products") || "[]");
    renderProducts(products);
  }

  // Initial load of products
  loadProducts();

  // DOM Elements
  const addProductBtn = document.getElementById("addProductBtn");
  const productModal = document.getElementById("productModal");
  const closeModalBtns = document.querySelectorAll(".close-modal");
  const productForm = document.getElementById("productForm");
  const imageUpload = document.getElementById("imageUpload");
  const imagePreview = document.getElementById("imagePreview");
  const searchInput = document.querySelector(".search-box input");
  const categoryFilter = document.getElementById("filterCategory");
  const statusFilter = document.getElementById("filterStatus");

  // Get products from localStorage
  let products = JSON.parse(localStorage.getItem("products") || "[]");

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
      (p) => p.stock === 0 || p.status === "out-of-stock"
    ).length;
    const active = products.filter((p) => p.status === "active").length;
    document.getElementById("countAll").textContent = total;
    document.getElementById("countOut").textContent = out;
    document.getElementById("countActive").textContent = active;
  }

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

  // Event Listeners
  addProductBtn.addEventListener("click", () => {
    // Redirect to add product page
    window.location.href = "/seller/add_product";
  });

  closeModalBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      productModal.classList.remove("active");
    });
  });

  // Close modal when clicking outside
  productModal.addEventListener("click", (e) => {
    if (e.target === productModal) {
      productModal.classList.remove("active");
    }
  });

  // Handle form submission
  productForm.addEventListener("submit", (e) => {
    e.preventDefault();
    // Build product object from form (frontend-only for now)
    const product = {
      id: Date.now(),
      name: document.getElementById("productName").value,
      category: document.getElementById("productCategory").value,
      price: parseFloat(document.getElementById("productPrice").value) || 0,
      stock: parseInt(document.getElementById("productStock").value) || 0,
      status: "active",
      image:
        imagePreview.querySelector("img")?.src ||
        "/static/images/placeholder.svg",
    };
    products.unshift(product);
    renderProducts(products);
    productModal.classList.remove("active");
  });

  // Image upload handling
  imageUpload.addEventListener("click", () => {
    const input = imageUpload.querySelector('input[type="file"]');
    input.click();
  });

  imageUpload
    .querySelector('input[type="file"]')
    .addEventListener("change", (e) => {
      const files = e.target.files;
      handleImageFiles(files);
    });

  // Drag and drop handling
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

  // Filter handling
  searchInput.addEventListener("input", filterProducts);
  categoryFilter.addEventListener("change", filterProducts);
  statusFilter.addEventListener("change", filterProducts);

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

  // Functions
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

  // Make edit/delete buttons work (delegated)
  document
    .getElementById("productTableBody")
    ?.addEventListener("click", function (e) {
      const editBtn = e.target.closest(".edit-product");
      const delBtn = e.target.closest(".delete-product");
      if (editBtn) {
        const id = parseInt(editBtn.dataset.id);
        const p = products.find((x) => x.id === id);
        if (p) {
          // populate form
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

  // Selection / bulk actions
  const selectAll = document.getElementById("selectAll");
  const bulkActions = document.getElementById("bulkActions");

  function getSelectedIds() {
    return Array.from(document.querySelectorAll(".row-select:checked")).map(
      (cb) => parseInt(cb.dataset.id)
    );
  }

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

  function filterProducts() {
    const searchTerm = searchInput.value.toLowerCase();
    const categoryValue = categoryFilter.value;
    const statusValue = statusFilter.value;

    const filteredProducts = products.filter((product) => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm);
      const matchesCategory =
        !categoryValue || product.category === categoryValue;
      const matchesStatus = !statusValue || product.status === statusValue;
      return matchesSearch && matchesCategory && matchesStatus;
    });

    renderProducts(filteredProducts);
  }

  function renderProducts(productsToRender) {
    const tbody = document.getElementById("productTableBody");
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
                          product.image || "/static/images/placeholder.svg"
                        }" alt="${product.name}" class="product-image">
                        <span class="product-name">${product.name}</span>
                    </div>
                </td>
                <td>${product.category}</td>
                <td>$${product.price.toFixed(2)}</td>
                <td>${product.stock}</td>
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

    // Reinitialize Lucide icons for the new content
    if (window.lucide) {
      lucide.createIcons();
    }
    // update counts after re-render
    updateCounts();
  }

  // Initial render
  renderProducts(products);
});
