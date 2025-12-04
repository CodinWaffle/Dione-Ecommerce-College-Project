// Delivery Management Page JS

document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("deliveryTableBody");
  const proofModal = document.getElementById("proofOfDeliveryModal");
  const modalCloseBtn = proofModal?.querySelector("[data-close-modal]");
  const proofForm = document.getElementById("proofOfDeliveryForm");
  const modalDeliveryId = document.getElementById("modalDeliveryId");
  const paymentCheckbox = document.getElementById("paymentReceivedToggle");
  const searchInput = document.getElementById("deliverySearchInput");
  const shiftCard = document.getElementById("deliveryShiftStatus");
  const shiftLabel = shiftCard?.querySelector(".shift-label");
  const shiftBadge = shiftCard?.querySelector(".shift-badge");
  const shiftMessage = shiftCard?.querySelector(".shift-message");

  const SHIFT_MESSAGES = {
    on: "Deliveries near your assigned zones will appear below.",
    off: "Switch to an active shift on your profile to receive new delivery offers.",
  };

  let refreshPromise = null;

  async function refreshDeliveries() {
    if (!tableBody || refreshPromise) {
      return refreshPromise;
    }
    refreshPromise = (async () => {
      try {
        const [availablePayload, assignedPayload] = await Promise.all([
          fetchDeliveries("available"),
          fetchDeliveries("assigned"),
        ]);
        updateShiftCard(availablePayload);
        const deliveries = mergeDeliveries(
          availablePayload.deliveries,
          assignedPayload.deliveries
        );
        renderDeliveryTable(deliveries);
      } catch (error) {
        renderTableError(error.message);
        console.error(error);
      } finally {
        refreshPromise = null;
      }
    })();
    return refreshPromise;
  }

  async function fetchDeliveries(scope) {
    const response = await fetch(`/rider/api/deliveries?scope=${scope}`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      cache: "no-store",
    });
    const payload = await parseJsonResponse(response);
    if (!response.ok || !payload.success) {
      throw new Error(payload?.error || "Unable to load deliveries.");
    }
    return payload;
  }

  function mergeDeliveries(available = [], assigned = []) {
    const orderedMap = new Map();
    assigned.forEach((delivery) => orderedMap.set(delivery.id, delivery));
    available.forEach((delivery) => {
      if (!orderedMap.has(delivery.id)) {
        orderedMap.set(delivery.id, delivery);
      }
    });
    return Array.from(orderedMap.values());
  }

  function renderDeliveryTable(deliveries) {
    if (!tableBody) return;
    tableBody.innerHTML = "";
    if (!deliveries.length) {
      tableBody.innerHTML =
        '<tr><td colspan="7" class="text-center muted">No deliveries assigned yet.</td></tr>';
      return;
    }
    deliveries.forEach((delivery) => {
      const row = buildDeliveryRow(delivery);
      tableBody.appendChild(row);
    });
    if (searchInput && searchInput.value.trim()) {
      searchInput.dispatchEvent(new Event("input"));
    }
  }

  function renderTableError(message) {
    if (!tableBody) return;
    tableBody.innerHTML = "";
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 7;
    cell.className = "text-center muted";
    cell.textContent = message;
    row.appendChild(cell);
    tableBody.appendChild(row);
  }

  function buildDeliveryRow(delivery) {
    const row = document.createElement("tr");
    row.dataset.deliveryId = delivery.id;
    row.dataset.rawStatus = delivery.raw_status;
    row.dataset.assigned = delivery.assigned_to_me ? "1" : "0";
    row.dataset.orderStatus = delivery.order_status || "";
    row.classList.toggle(
      "order-in-transit",
      delivery.order_status === "in_transit"
    );

    [
      delivery.order_number,
      delivery.customer_name,
      delivery.address,
      delivery.contact,
      delivery.payment_method,
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value || "—";
      row.appendChild(cell);
    });

    row.appendChild(buildStatusCell(delivery));
    row.appendChild(buildActionCell());
    toggleActionButtons(row, delivery);
    return row;
  }

  function buildStatusCell(delivery) {
    const statusCell = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = `status-badge delivery-status-badge status-${(
      delivery.raw_status || ""
    ).replace(/\s+/g, "-")}`;
    badge.textContent = delivery.status;
    statusCell.appendChild(badge);

    const formattedOrderStatus = formatOrderStatus(delivery.order_status);
    if (formattedOrderStatus) {
      const orderStatus = document.createElement("small");
      orderStatus.className = "order-status-label";
      orderStatus.textContent = formattedOrderStatus;
      statusCell.appendChild(orderStatus);
    }
    return statusCell;
  }

  function buildActionCell() {
    const actionsCell = document.createElement("td");
    actionsCell.innerHTML = `
      <div class="action-buttons-group">
        <button class="action-btn accept-delivery-btn" title="Accept delivery">
          <span class="material-symbols-outlined">task_alt</span>
        </button>
        <button class="action-btn reject-delivery-btn" title="Reject delivery">
          <span class="material-symbols-outlined">close</span>
        </button>
        <button class="action-btn mark-today-btn" title="Mark as To Receive Today">
          <span class="material-symbols-outlined">event_available</span>
        </button>
        <button class="action-btn complete-delivery-btn" title="Complete delivery">
          <span class="material-symbols-outlined">camera_alt</span>
        </button>
      </div>
    `;
    return actionsCell;
  }

  function updateShiftCard(payload) {
    if (!shiftCard || !payload) return;
    const onShift = Boolean(payload.on_shift);
    if (shiftLabel) {
      shiftLabel.textContent =
        payload.shift_label || formatOrderStatus(payload.shift_value);
    }
    if (shiftBadge) {
      shiftBadge.textContent = onShift ? "Active" : "Off Shift";
      shiftBadge.classList.toggle("success", onShift);
      shiftBadge.classList.toggle("warning", !onShift);
    }
    if (shiftMessage) {
      shiftMessage.textContent = onShift
        ? SHIFT_MESSAGES.on
        : SHIFT_MESSAGES.off;
    }
    shiftCard.classList.toggle("on-shift", onShift);
    shiftCard.classList.toggle("off-shift", !onShift);
  }

  refreshDeliveries();
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      refreshDeliveries();
    }
  });
  window.addEventListener("focus", () => refreshDeliveries());

  tableBody?.addEventListener("click", async (event) => {
    const row = event.target.closest("tr[data-delivery-id]");
    if (!row) return;
    const deliveryId = row.dataset.deliveryId;

    if (event.target.closest(".accept-delivery-btn")) {
      event.preventDefault();
      await handleAcceptDelivery(row, deliveryId);
      return;
    }
    if (event.target.closest(".reject-delivery-btn")) {
      event.preventDefault();
      await handleRejectDelivery(row, deliveryId);
      return;
    }
    if (event.target.closest(".mark-today-btn")) {
      event.preventDefault();
      await handleStatusUpdate(row, deliveryId, "to_receive_today");
      return;
    }
    if (event.target.closest(".complete-delivery-btn")) {
      event.preventDefault();
      openProofModal(deliveryId);
    }
  });

  modalCloseBtn?.addEventListener("click", closeProofModal);
  window.addEventListener("click", (event) => {
    if (event.target === proofModal) closeProofModal();
  });

  proofForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const deliveryId = modalDeliveryId.value;
    if (!deliveryId) return;
    if (!paymentCheckbox.checked) {
      alert("Please confirm payment before completing delivery.");
      return;
    }
    const fileInput = document.getElementById("photoUpload");
    if (!fileInput.files.length) {
      alert("Please upload a delivery photo.");
      return;
    }

    const formData = new FormData();
    formData.append("status", "delivered");
    formData.append("payment_received", "true");
    formData.append("photo", fileInput.files[0]);
    formData.append(
      "notes",
      document.getElementById("deliveryNotes").value || ""
    );

    try {
      const response = await fetch(
        `/rider/api/deliveries/${deliveryId}/status`,
        {
          method: "POST",
          body: formData,
        }
      );
      const payload = await parseJsonResponse(response);
      if (!response.ok || !payload.success) {
        throw new Error(payload?.error || "Unable to complete delivery.");
      }
      updateDeliveryRow(deliveryId, payload.delivery);
      closeProofModal(true);
      refreshDeliveries();
    } catch (error) {
      alert(error.message);
    }
  });

  searchInput?.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    Array.from(
      tableBody?.querySelectorAll("tr[data-delivery-id]") || []
    ).forEach((row) => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(query) ? "" : "none";
    });
  });

  function openProofModal(deliveryId) {
    modalDeliveryId.value = deliveryId;
    proofModal.style.display = "block";
  }

  function closeProofModal(resetFields = false) {
    proofModal.style.display = "none";
    if (resetFields) {
      proofForm.reset();
    }
  }
  async function handleAcceptDelivery(row, deliveryId) {
    row.classList.add("is-processing");
    try {
      const response = await fetch(
        `/rider/api/deliveries/${deliveryId}/accept`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );
      const payload = await parseJsonResponse(response);
      if (!response.ok || !payload.success) {
        throw new Error(payload?.error || "Unable to accept delivery.");
      }
      updateDeliveryRow(deliveryId, payload.delivery);
      refreshDeliveries();
    } catch (error) {
      alert(error.message);
    } finally {
      row.classList.remove("is-processing");
    }
  }

  async function handleRejectDelivery(row, deliveryId) {
    const reason = prompt("Reason for rejection? (optional)") || "";
    try {
      const response = await fetch(
        `/rider/api/deliveries/${deliveryId}/reject`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reason }),
        }
      );
      const payload = await parseJsonResponse(response);
      if (!response.ok || !payload.success) {
        throw new Error(payload?.error || "Unable to reject delivery.");
      }
      updateDeliveryRow(deliveryId, payload.delivery);
      refreshDeliveries();
    } catch (error) {
      alert(error.message);
    }
  }

  async function handleStatusUpdate(row, deliveryId, status) {
    try {
      const response = await fetch(
        `/rider/api/deliveries/${deliveryId}/status`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status }),
        }
      );
      const payload = await parseJsonResponse(response);
      if (!response.ok || !payload.success) {
        throw new Error(payload?.error || "Unable to update delivery status.");
      }
      updateDeliveryRow(deliveryId, payload.delivery);
      refreshDeliveries();
    } catch (error) {
      alert(error.message);
    }
  }

  function updateDeliveryRow(deliveryId, delivery) {
    const row = document.querySelector(`tr[data-delivery-id="${deliveryId}"]`);
    if (!row || !delivery) return;

    row.dataset.rawStatus = delivery.raw_status;
    row.dataset.assigned = delivery.assigned_to_me ? "1" : "0";
    row.dataset.orderStatus = delivery.order_status || "";
    row.classList.toggle(
      "order-in-transit",
      delivery.order_status === "in_transit"
    );
    row.querySelector("td:nth-child(1)").textContent = delivery.order_number;
    row.querySelector("td:nth-child(2)").textContent = delivery.customer_name;
    row.querySelector("td:nth-child(3)").textContent = delivery.address;
    row.querySelector("td:nth-child(4)").textContent = delivery.contact;
    row.querySelector("td:nth-child(5)").textContent = delivery.payment_method;

    const statusBadge = row.querySelector(".delivery-status-badge");
    if (statusBadge) {
      statusBadge.textContent = delivery.status;
      statusBadge.className = `status-badge delivery-status-badge status-${delivery.raw_status.replace(
        /\s+/g,
        "-"
      )}`;
    }

    syncOrderStatusLabel(row, delivery);
    toggleActionButtons(row, delivery);
  }

  function syncOrderStatusLabel(row, delivery) {
    const formatted = formatOrderStatus(delivery.order_status);
    const statusCell = row.querySelector(
      ".delivery-status-badge"
    )?.parentElement;
    if (!statusCell) return;
    let label = statusCell.querySelector(".order-status-label");
    if (formatted) {
      if (!label) {
        label = document.createElement("small");
        label.className = "order-status-label";
        statusCell.appendChild(label);
      }
      label.textContent = formatted;
      label.style.display = "inline";
    } else if (label) {
      label.remove();
    }
  }

  function toggleActionButtons(row, delivery) {
    const acceptBtn = row.querySelector(".accept-delivery-btn");
    const rejectBtn = row.querySelector(".reject-delivery-btn");
    const markTodayBtn = row.querySelector(".mark-today-btn");
    const completeBtn = row.querySelector(".complete-delivery-btn");

    const rawStatus = delivery.raw_status;
    const assigned = delivery.assigned_to_me;
    const readyStatuses = [
      "ready_for_delivery",
      "delivery_rejected",
      "picked_up",
    ];

    if (acceptBtn) {
      acceptBtn.style.display =
        !assigned && readyStatuses.includes(rawStatus) ? "" : "none";
    }

    if (rejectBtn) {
      rejectBtn.style.display = assigned ? "" : "none";
    }

    if (markTodayBtn) {
      markTodayBtn.style.display =
        assigned &&
        rawStatus !== "to_receive_today" &&
        rawStatus !== "delivered"
          ? ""
          : "none";
    }

    if (completeBtn) {
      completeBtn.style.display =
        assigned && rawStatus !== "delivered" ? "" : "none";
    }
  }
});

function formatOrderStatus(status) {
  if (!status) return "";
  return status
    .split(/[-_]/)
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

async function parseJsonResponse(response) {
  const text = await response.text();
  if (!text) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    const snippet = text.replace(/\s+/g, " ").trim().slice(0, 140);
    const looksHtml =
      snippet.startsWith("<") || snippet.toLowerCase().startsWith("<!doctype");
    const hint = looksHtml
      ? "Received HTML instead of JSON (session may have expired)."
      : "Server returned an unreadable response.";
    throw new Error(`${hint}${snippet ? ` Details: ${snippet}` : ""}`);
  }
}
