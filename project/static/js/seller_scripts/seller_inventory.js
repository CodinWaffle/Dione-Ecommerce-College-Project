/**
 * Seller Inventory Management
 * New design with tabs, improved modals, and cleaner interactions.
 */

document.addEventListener("DOMContentLoaded", function () {
  initNotifications();
  initInventoryTable();
  initModals();
  initForms();
  updateInventoryStats();
});

/**
 * Initializes all functionalities related to the inventory table.
 */
function initInventoryTable() {
  const searchInput = document.getElementById("inventorySearch");
  searchInput?.addEventListener("input", filterAndSortTable);

  const sortSelect = document.getElementById("sortInventory");
  sortSelect?.addEventListener("change", filterAndSortTable);

  document.querySelectorAll(".tab-btn").forEach((button) => {
    button.addEventListener("click", function () {
      document.querySelector(".tab-btn.active").classList.remove("active");
      this.classList.add("active");
      filterAndSortTable();
    });
  });

  initRowSelection();
  initBatchActions();
  initPagination();
  initQuickEdit();
  initActionButtons();
}

/**
 * Initializes event listeners for individual row action buttons (edit, delete).
 */
function initActionButtons() {
  document.getElementById("inventoryTable")?.addEventListener("click", (e) => {
    const editBtn = e.target.closest(".edit-btn");
    if (editBtn) {
      const inventoryId = editBtn.getAttribute("data-id");
      openEditInventoryModal(inventoryId);
    }

    const deleteBtn = e.target.closest(".delete-btn");
    if (deleteBtn) {
      const inventoryId = deleteBtn.getAttribute("data-id");
      openDeleteConfirmationModal(inventoryId);
    }
  });
}

/**
 * Initializes row selection behavior (select all, individual select).
 */
function initRowSelection() {
  const selectAllHeader = document.getElementById("selectAllHeader");
  selectAllHeader?.addEventListener("change", (e) => {
    const isChecked = e.target.checked;
    document
      .querySelectorAll("#inventoryTable tbody .row-checkbox")
      .forEach((checkbox) => {
        checkbox.checked = isChecked;
      });
    updateBatchActionButtons();
  });

  document.getElementById("inventoryTable")?.addEventListener("change", (e) => {
    if (e.target.classList.contains("row-checkbox")) {
      updateBatchActionButtons();
      updateSelectAllCheckbox();
    }
  });
}

/**
 * Filters and sorts the inventory table based on current control values.
 */
function filterAndSortTable() {
  const searchValue = document
    .getElementById("inventorySearch")
    .value.toLowerCase();
  const statusFilter = document.querySelector(".tab-btn.active").dataset.status;
  const sortValue = document.getElementById("sortInventory").value;

  const tbody = document.querySelector("#inventoryTable tbody");
  if (!tbody) return;

  const rows = Array.from(tbody.querySelectorAll("tr"));

  // 1. Filter rows
  rows.forEach((row) => {
    const productName = row
      .querySelector(".product-name")
      .textContent.toLowerCase();
    const sku = row.querySelector(".product-sku").textContent.toLowerCase();
    const stockStatus = row.getAttribute("data-stock-status");

    const matchesSearch =
      productName.includes(searchValue) || sku.includes(searchValue);
    const matchesStatus =
      statusFilter === "all" || stockStatus === statusFilter;

    if (matchesSearch && matchesStatus) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });

  // 2. Sort visible rows
  rows.sort((a, b) => {
    const nameA = a.querySelector(".product-name").textContent;
    const nameB = b.querySelector(".product-name").textContent;
    const stockA = parseInt(a.getAttribute("data-stock"));
    const stockB = parseInt(b.getAttribute("data-stock"));

    switch (sortValue) {
      case "name_asc":
        return nameA.localeCompare(nameB);
      case "name_desc":
        return nameB.localeCompare(nameA);
      case "stock_asc":
        return stockA - stockB;
      case "stock_desc":
        return stockB - stockA;
      default:
        return 0;
    }
  });

  // 3. Re-append sorted rows and update table state
  rows.forEach((row) => tbody.appendChild(row));
  updateTableEmptyState();
  initPagination(); // Re-initialize pagination after filtering/sorting
}

/**
 * Initialize batch actions functionality
 */
function initBatchActions() {
  document.getElementById("batchUpdateBtn")?.addEventListener("click", () => {
    const selectedRows = getSelectedRows();
    if (selectedRows.length > 0) {
      openBatchUpdateModal(selectedRows);
    }
  });

  document.getElementById("batchDeleteBtn")?.addEventListener("click", () => {
    const selectedRows = getSelectedRows();
    if (selectedRows.length > 0) {
      openBatchDeleteModal(selectedRows);
    }
  });
}

/**
 * Get all selected rows from the inventory table
 * @returns {Array} Array of selected row elements
 */
function getSelectedRows() {
  return Array.from(
    document.querySelectorAll("#inventoryTable tbody .row-checkbox:checked")
  ).map((checkbox) => checkbox.closest("tr"));
}

/**
 * Update the state of the batch action buttons based on selection
 */
function updateBatchActionButtons() {
  const selectedRows = getSelectedRows();
  const batchUpdateBtn = document.getElementById("batchUpdateBtn");
  const batchDeleteBtn = document.getElementById("batchDeleteBtn");

  if (batchUpdateBtn) {
    batchUpdateBtn.disabled = selectedRows.length === 0;
  }
  if (batchDeleteBtn) {
    batchDeleteBtn.disabled = selectedRows.length === 0;
  }
}

/**
 * Update the state of the select all checkbox
 */
function updateSelectAllCheckbox() {
  const selectAllCheckbox = document.getElementById("selectAll");
  const rowCheckboxes = document.querySelectorAll(
    "#inventoryTable tbody .row-checkbox"
  );
  const checkedCount = document.querySelectorAll(
    "#inventoryTable tbody .row-checkbox:checked"
  ).length;

  if (selectAllCheckbox) {
    if (checkedCount === 0) {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === rowCheckboxes.length) {
      selectAllCheckbox.checked = true;
      selectAllCheckbox.indeterminate = false;
    } else {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = true;
    }
  }
}

/**
 * Initializes pagination functionality.
 */
function initPagination() {
  const table = document.getElementById("inventoryTable");
  if (!table) return;

  // Prefer the shared TableFooter component if available. It provides a
  // reusable pagination UI and callback. Otherwise, fall back to local logic.
  const footerContainer = document.querySelector(".component-table-footer");
  const rowsPerPage = 10;

  if (window.TableFooter && footerContainer) {
    // build rows array of visible rows
    const allRows = Array.from(table.querySelectorAll("tbody tr"));
    const visibleRows = () => allRows.filter((r) => r.style.display !== "none");

    const tf = TableFooter.create(footerContainer, {
      itemsPerPage: rowsPerPage,
      onPageChange(page) {
        // show correct slice of visible rows
        const rows = visibleRows();
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        rows.forEach(
          (row, idx) =>
            (row.style.display = idx >= start && idx < end ? "" : "none")
        );
      },
    });

    // initialize with current visible count
    tf.update(visibleRows().length);
    // Keep reference for other parts to call update when filters change
    window.__inventoryTableFooter = { widget: tf, visibleRows };
    return;
  }

  // Fallback (existing behaviour)
  let currentPage = 1;
  const rows = Array.from(
    table.querySelectorAll("tbody tr:not([style*='display: none'])")
  );
  const totalRows = rows.length;
  const totalPages = Math.ceil(totalRows / rowsPerPage);

  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const paginationNumbers = document.getElementById("paginationNumbers");
  const showingItems = document.getElementById("showingItems");
  const totalItemsCount = document.getElementById("totalItemsCount");

  function displayRows() {
    rows.forEach((row, index) => {
      row.style.display = "none";
      const start = (currentPage - 1) * rowsPerPage;
      const end = start + rowsPerPage;
      if (index >= start && index < end) {
        row.style.display = "";
      }
    });
    updatePaginationUI();
  }

  function updatePaginationUI() {
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages || totalPages === 0;

    const startItem = totalRows > 0 ? (currentPage - 1) * rowsPerPage + 1 : 0;
    const endItem = Math.min(currentPage * rowsPerPage, totalRows);
    showingItems.textContent = `${startItem}-${endItem}`;
    totalItemsCount.textContent = totalRows;

    paginationNumbers.innerHTML = "";
    for (let i = 1; i <= totalPages; i++) {
      const pageBtn = document.createElement("button");
      pageBtn.className = "page-number";
      pageBtn.textContent = i;
      if (i === currentPage) {
        pageBtn.classList.add("active");
      }
      pageBtn.addEventListener("click", () => {
        currentPage = i;
        displayRows();
      });
      paginationNumbers.appendChild(pageBtn);
    }
  }

  prevBtn.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      displayRows();
    }
  });

  nextBtn.addEventListener("click", () => {
    if (currentPage < totalPages) {
      currentPage++;
      displayRows();
    }
  });

  displayRows();
}

/**
 * Initialize modals
 */
function initModals() {
  const addInventoryBtn = document.getElementById("addInventoryBtn");
  const addInventoryModal = document.getElementById("addInventoryModal");
  addInventoryBtn?.addEventListener("click", () =>
    openModal(addInventoryModal)
  );

  document.querySelectorAll(".modal-close, .modal-cancel").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modalId = btn.dataset.modalId;
      const modal = document.getElementById(modalId);
      if (modal) {
        closeModal(modal);
      }
    });
  });

  window.addEventListener("click", function (event) {
    const modals = document.querySelectorAll(".modal");
    modals.forEach((modal) => {
      if (event.target === modal) {
        closeModal(modal);
      }
    });
  });
}

/**
 * Open a modal
 * @param {HTMLElement} modal The modal element to open
 */
function openModal(modal) {
  modal?.classList.add("active");
  document.body.classList.add("modal-open");
}

/**
 * Close a modal
 * @param {HTMLElement} modal The modal element to close
 */
function closeModal(modal) {
  modal?.classList.remove("active");
  document.body.classList.remove("modal-open");
}

/**
 * Open the edit inventory modal for a specific inventory item
 * @param {string} inventoryId The ID of the inventory item to edit
 */
function openEditInventoryModal(inventoryId) {
  const modal = document.getElementById("editInventoryModal");

  if (!modal) return;

  // Find inventory data from the table
  const row = document.querySelector(`tr[data-id="${inventoryId}"]`);
  if (!row) return;

  const productName = row.querySelector(".product-name").textContent;
  const sku = row
    .querySelector(".product-sku")
    .textContent.replace("SKU: ", "");
  const currentStock = row.getAttribute("data-stock");
  const threshold = row.getAttribute("data-threshold");

  // Populate form fields
  document.getElementById("editInventoryId").value = inventoryId;
  document.getElementById("editProductName").value = productName;
  document.getElementById("editSku").value = sku;
  document.getElementById("editCurrentStock").value = currentStock;
  document.getElementById("editThreshold").value = threshold;

  // Update modal title
  document.getElementById(
    "editModalTitle"
  ).textContent = `Edit: ${productName}`;

  // Open the modal
  openModal(modal);
}

/**
 * Open delete confirmation modal
 * @param {string} inventoryId The ID of the inventory item to delete
 */
function openDeleteConfirmationModal(inventoryId) {
  const modal = document.getElementById("deleteConfirmationModal");

  if (!modal) return;

  // Find product name from the table
  const row = document.querySelector(`tr[data-id="${inventoryId}"]`);
  if (!row) return;

  const productName = row.querySelector(".product-name").textContent;

  // Set inventory ID in the form
  document.getElementById("deleteInventoryId").value = inventoryId;

  // Update confirmation message
  document.getElementById(
    "deleteConfirmationMessage"
  ).innerHTML = `Are you sure you want to delete inventory for <strong>"${productName}"</strong>? This action cannot be undone.`;

  // Open the modal
  openModal(modal);
}

/**
 * Open batch update modal
 * @param {Array} selectedRows The selected rows to update
 */
function openBatchUpdateModal(selectedRows) {
  const modal = document.getElementById("batchUpdateModal");

  if (!modal) return;

  // Update the count of selected items
  const itemCount = selectedRows.length;
  document.getElementById("batchUpdateCount").textContent = itemCount;

  // Create list of selected products
  const productsList = document.getElementById("selectedProductsList"); // Corrected ID
  productsList.innerHTML = "";

  selectedRows.forEach((row) => {
    const productName = row.querySelector(".product-name").textContent;
    const listItem = document.createElement("li");
    listItem.textContent = productName;
    productsList.appendChild(listItem);
  });

  // Store selected IDs
  const selectedIds = selectedRows.map((row) => row.getAttribute("data-id"));
  document.getElementById("batchSelectedIds").value =
    JSON.stringify(selectedIds);

  // Open the modal
  openModal(modal);
}

/**
 * Open batch delete modal
 * @param {Array} selectedRows The selected rows to delete
 */
function openBatchDeleteModal(selectedRows) {
  const modal = document.getElementById("batchDeleteModal");

  if (!modal) return;

  // Update the count of selected items
  const itemCount = selectedRows.length;
  document.getElementById("batchDeleteCount").textContent = itemCount;

  // Create list of selected products
  const productsList = document.getElementById("batchDeleteProductsList"); // Corrected ID
  productsList.innerHTML = "";

  selectedRows.forEach((row) => {
    const productName = row.querySelector(".product-name").textContent;
    const listItem = document.createElement("li");
    listItem.textContent = productName;
    productsList.appendChild(listItem);
  });

  // Store selected IDs
  const selectedIds = selectedRows.map((row) => row.getAttribute("data-id"));
  document.getElementById("batchDeleteSelectedIds").value =
    JSON.stringify(selectedIds);

  // Open the modal
  openModal(modal);
}

/**
 * Initialize forms
 */
function initForms() {
  document
    .getElementById("addInventoryForm")
    ?.addEventListener("submit", (e) => {
      e.preventDefault();
      submitAddInventoryForm();
    });

  document
    .getElementById("editInventoryForm")
    ?.addEventListener("submit", (e) => {
      e.preventDefault();
      submitEditInventoryForm();
    });

  document
    .getElementById("deleteInventoryForm")
    ?.addEventListener("submit", (e) => {
      e.preventDefault();
      submitDeleteInventoryForm();
    });

  document
    .getElementById("batchUpdateForm")
    ?.addEventListener("submit", (e) => {
      e.preventDefault();
      submitBatchUpdateForm();
    });

  document
    .getElementById("batchDeleteForm")
    ?.addEventListener("submit", (e) => {
      e.preventDefault();
      submitBatchDeleteForm();
    });
}

/**
 * Submit add inventory form
 */
function submitAddInventoryForm() {
  const form = document.getElementById("addInventoryForm");
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalBtnText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="loader"></span> Adding...';

  const productId = document.getElementById("productId").value;
  const currentStock = document.getElementById("currentStock").value;
  const threshold = document.getElementById("threshold").value;

  fetch("/api/seller/inventory/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ productId, currentStock, threshold }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        showNotification("success", "Inventory Added", data.message);
        closeModal(document.getElementById("addInventoryModal"));
        // Instead of reloading, we can add the new row dynamically
        // For simplicity, we'll reload for now to get all updated data from server
        setTimeout(() => window.location.reload(), 500);
      } else {
        showNotification("error", "Error", data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification(
        "error",
        "Network Error",
        "Could not connect to the server."
      );
    })
    .finally(() => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    });
}

/**
 * Creates and appends a new inventory row to the table.
 * @param {object} item The new inventory item data from the server.
 */
function addRowToTable(item) {
  const tbody = document.querySelector("#inventoryTable tbody");
  const newRow = document.createElement("tr");
  newRow.setAttribute("data-id", item.id);
  newRow.setAttribute("data-stock", item.stock);
  newRow.setAttribute("data-threshold", item.low_stock_threshold);

  const stockStatusInfo = getStockStatusInfo(
    item.stock,
    item.low_stock_threshold
  );
  newRow.setAttribute("data-stock-status", stockStatusInfo.class);

  newRow.innerHTML = `
    <td><input type="checkbox" class="row-checkbox" /></td>
    <td>
      <div class="product-cell">
        <img class="product-image" src="/static/images/products/${item.image}" alt="${item.product}" />
        <span class="product-name">${item.product}</span>
      </div>
    </td>
    <td><span class="product-sku">${item.sku}</span></td>
    <td class="stock-cell">
      <span class="stock-value">${item.stock}</span>
      <button class="action-btn quick-edit-btn" title="Quick edit stock" data-field="stock"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>
    </td>
    <td><span class="threshold-badge">${item.low_stock_threshold}</span></td>
    <td><span class="stock-status ${stockStatusInfo.class}">${stockStatusInfo.text}</span></td>
    <td class="action-cell">
      <div class="action-buttons">
        <button class="action-btn edit-btn" title="Edit" data-id="${item.id}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>
        <button class="action-btn delete-btn" title="Delete" data-id="${item.id}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg></button>
      </div>
    </td>
  `;
  tbody.prepend(newRow);
  updateTableEmptyState();
  updateInventoryStats();
  initPagination();
}

/**
 * Submits the edit inventory form.
 */
function submitEditInventoryForm() {
  // Get form data
  const inventoryId = document.getElementById("editInventoryId").value;
  const currentStock = document.getElementById("editCurrentStock").value;
  const threshold = document.getElementById("editThreshold").value;

  fetch(`/api/seller/inventory/edit/${inventoryId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ currentStock, threshold }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        const row = document.querySelector(`tr[data-id="${inventoryId}"]`);
        if (row) {
          row.setAttribute("data-stock", data.item.stock);
          row.setAttribute("data-threshold", data.item.low_stock_threshold);
          row.querySelector(".stock-value").textContent = data.item.stock;
          row.querySelector(".threshold-badge").textContent =
            data.item.low_stock_threshold;
          updateStockStatus(
            row,
            data.item.stock,
            data.item.low_stock_threshold
          );
        }
        showNotification("success", "Inventory Updated", data.message);
        closeModal(document.getElementById("editInventoryModal"));
        updateInventoryStats();
        filterAndSortTable();
      } else {
        showNotification("error", "Update Failed", data.message);
      }
    })
    .catch((err) => console.error(err));
}

/**
 * Submits the delete inventory form.
 */
function submitDeleteInventoryForm() {
  // Get inventory ID
  const inventoryId = document.getElementById("deleteInventoryId").value;

  fetch(`/api/seller/inventory/delete/${inventoryId}`, { method: "DELETE" })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        const row = document.querySelector(`tr[data-id="${inventoryId}"]`);
        row?.remove();
        showNotification("success", "Inventory Deleted", data.message);
        closeModal(document.getElementById("deleteConfirmationModal"));
        updateTableEmptyState();
        updateInventoryStats();
        initPagination();
      } else {
        showNotification("error", "Delete Failed", data.message);
      }
    })
    .catch((err) => console.error(err));
}

/**
 * Submits the batch update form.
 */
function submitBatchUpdateForm() {
  // Get form data
  const ids = JSON.parse(document.getElementById("batchSelectedIds").value);
  const updateAction = document.getElementById("batchUpdateAction").value;
  const updateValue = document.getElementById("batchUpdateValue").value;

  fetch("/api/seller/inventory/batch-update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids, action: updateAction, value: updateValue }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        data.updated_items.forEach((item) => {
          const row = document.querySelector(`tr[data-id="${item.id}"]`);
          if (row) {
            row.setAttribute("data-stock", item.stock);
            row.setAttribute("data-threshold", item.low_stock_threshold);
            row.querySelector(".stock-value").textContent = item.stock;
            row.querySelector(".threshold-badge").textContent =
              item.low_stock_threshold;
            updateStockStatus(row, item.stock, item.low_stock_threshold);
          }
        });

        showNotification("success", "Batch Update Complete", data.message);
        closeModal(document.getElementById("batchUpdateModal"));

        document.getElementById("selectAllHeader").checked = false;
        document
          .querySelectorAll(".row-checkbox:checked")
          .forEach((cb) => (cb.checked = false));

        updateBatchActionButtons();
        updateInventoryStats();
        filterAndSortTable();
      } else {
        showNotification("error", "Batch Update Failed", data.message);
      }
    })
    .catch((err) => console.error(err));
}

/**
 * Submits the batch delete form.
 */
function submitBatchDeleteForm() {
  // Get selected IDs
  const ids = JSON.parse(
    document.getElementById("batchDeleteSelectedIds").value
  );

  // TODO: Send delete request to server
  // For now, simulate success and update the UI

  fetch("/api/seller/inventory/batch-delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        ids.forEach((id) => {
          document.querySelector(`tr[data-id="${id}"]`)?.remove();
        });
        showNotification("success", "Batch Delete Complete", data.message);
        closeModal(document.getElementById("batchDeleteModal"));
        updateTableEmptyState();
        updateInventoryStats();
        initPagination();
      } else {
        showNotification("error", "Batch Delete Failed", data.message);
      }
    })
    .catch((err) => console.error(err));
}

/**
 * Update the stock status of a row
 * @param {HTMLElement} row The table row element
 * @param {number} stock The current stock
 * @param {number} threshold The low stock threshold
 */
function updateStockStatus(row, stock, threshold) {
  const statusCell = row?.querySelector(".stock-status");
  if (!statusCell) return;

  statusCell.classList.remove("in-stock", "low-stock", "out-of-stock");

  if (stock <= 0) {
    row.setAttribute("data-stock-status", "out-of-stock");
    statusCell.classList.add("out-of-stock");
    statusCell.textContent = "Out of Stock";
  } else if (stock <= threshold) {
    row.setAttribute("data-stock-status", "low-stock");
    statusCell.classList.add("low-stock");
    statusCell.textContent = "Low Stock";
  } else {
    row.setAttribute("data-stock-status", "in-stock");
    statusCell.classList.add("in-stock");
    statusCell.textContent = "In Stock";
  }
}

/**
 * Update table empty state
 */
function updateTableEmptyState() {
  const tableBody = document.querySelector("#inventoryTable tbody");
  if (!tableBody) return;

  const emptyState = document.getElementById("emptyState");
  const visibleRows = tableBody.querySelectorAll(
    'tr:not([style*="display: none"])'
  ).length;

  if (visibleRows === 0) {
    emptyState.style.display = "flex";
  } else {
    emptyState.style.display = "none";
  }
}

/**
 * Initialize quick edit functionality
 */
function initQuickEdit() {
  const quickEditButtons = document.querySelectorAll(".quick-edit-btn");
  quickEditButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.stopPropagation();
      const row = this.closest("tr");
      const field = this.getAttribute("data-field");
      const currentValue = parseInt(row.getAttribute(`data-${field}`));

      const input = document.createElement("input");
      input.type = "number";
      input.min = field === "stock" ? "0" : "1";
      input.className = "quick-edit-input";
      input.value = currentValue;

      const cell = this.parentElement;
      const originalContent = cell.innerHTML;
      cell.innerHTML = "";
      cell.appendChild(input);
      input.focus();

      const finishEdit = () => {
        finishQuickEdit(row, cell, field, originalContent, input.value);
      };

      input.addEventListener("blur", finishEdit);
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          input.blur();
        } else if (e.key === "Escape") {
          cell.innerHTML = originalContent;
        }
      });
    });
  });
}

/**
 * Finishes the quick edit operation, validates, and updates the UI.
 * @param {HTMLElement} row The table row element
 * @param {HTMLElement} cell The table cell element
 * @param {string} field The field being edited
 * @param {string} id The inventory ID
 * @param {string} originalContent The original cell content
 * @param {string} newValue The new value
 */
function finishQuickEdit(row, cell, field, originalContent, newValueStr) {
  const newValue = parseInt(newValueStr);
  const inventoryId = row.getAttribute("data-id");

  if (newValue === "" || isNaN(parseInt(newValue)) || parseInt(newValue) < 0) {
    cell.innerHTML = originalContent;
    showNotification("error", "Invalid Value", "Please enter a valid number.");
    return;
  }

  fetch(`/api/seller/inventory/quick-edit/${inventoryId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ field, value: newValue }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        row.setAttribute(`data-${field}`, newValue);
        cell.innerHTML = originalContent; // Restore original structure
        if (field === "stock") {
          cell.querySelector(".stock-value").textContent = newValue;
        } else {
          cell.querySelector(".threshold-badge").textContent = newValue;
        }
        updateStockStatus(row, data.item.stock, data.item.low_stock_threshold);
        updateInventoryStats();
        showNotification("success", "Update Successful", data.message);
      } else {
        cell.innerHTML = originalContent;
        showNotification("error", "Update Failed", data.message);
      }
    });
}

/**
 * Update inventory statistics
 */
function updateInventoryStats() {
  const allRows = document.querySelectorAll("#inventoryTable tbody tr");
  const totalItems = allRows.length;

  let inStockCount = 0;
  let lowStockCount = 0;
  allRows.forEach((row) => {
    const stock = parseInt(row.getAttribute("data-stock"));
    const threshold = parseInt(row.getAttribute("data-threshold"));
    if (stock > threshold) {
      inStockCount++;
    } else if (stock > 0 && stock <= threshold) {
      lowStockCount++;
    }
  });

  const outOfStockItems = document.querySelectorAll(
    'tr[data-stock-status="out-of-stock"]'
  ).length;
  const outOfStockElement = document.getElementById("outOfStockItems");
  if (outOfStockElement) {
    outOfStockElement.textContent = outOfStockItems;
  }

  document.getElementById("totalItems").textContent = totalItems;
  document.getElementById("inStockItems").textContent = inStockCount;
  document.getElementById("lowStockItems").textContent = lowStockCount;
  document.getElementById("outOfStockItems").textContent = outOfStockItems;
}

/**
 * Initialize notification system
 */
function initNotifications() {
  // Create notification container if it doesn't exist
  const container = document.createElement("div");
  container.className = "notification-container";
  document.body.appendChild(container);
}

/**
 * Show a notification
 * @param {string} type The notification type (success, error, warning)
 * @param {string} title The notification title
 * @param {string} message The notification message
 */
function showNotification(type, title, message) {
  const container = document.querySelector(".notification-container");
  const notification = document.createElement("div");

  notification.className = `notification ${type}`;

  // Set icon based on type
  let iconSvg;
  switch (type) {
    case "success":
      iconSvg =
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
      break;
    case "error":
      iconSvg =
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
      break;
    case "warning":
      iconSvg =
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>';
      break;
    default:
      iconSvg =
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
  }
  // Notification HTML
  notification.innerHTML = `
    <div class="notification-icon">${iconSvg}</div>
    <div class="notification-content">
      <div class="notification-title">${title}</div>
      <div class="notification-message">${message}</div>
    </div>
    <button class="notification-close">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  `;

  container.appendChild(notification);

  setTimeout(() => {
    notification.classList.add("show");
  }, 10);

  notification
    .querySelector(".notification-close")
    .addEventListener("click", () => {
      closeNotification(notification);
    });

  setTimeout(() => {
    closeNotification(notification);
  }, 5000);
}

/**
 * Close a notification
 * @param {HTMLElement} notification The notification element to close
 */
function closeNotification(notification) {
  if (notification) {
    notification.classList.remove("show");
    setTimeout(() => {
      notification.remove();
    }, 300);
  }
}
