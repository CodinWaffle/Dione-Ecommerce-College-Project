const STATUS_LABELS = {
  pending: "Pending",
  confirmed: "Confirmed",
  shipping: "To Ship",
  in_transit: "In Transit",
  delivered: "Delivered",
  completed: "Completed",
  cancelled: "Cancelled",
};

const PICKUP_STATUS_LABELS = {
  pending: "Pending",
  assigned: "Assigned",
  en_route: "En Route",
  picked_up: "Picked Up",
  completed: "Completed",
  cancelled: "Cancelled",
};

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".status-dropdown").forEach((dropdown) => {
    dropdown.addEventListener("change", handleStatusChange);
  });

  document.addEventListener("click", (event) => {
    const printButton = event.target.closest('[data-action="printLabel"]');
    if (printButton) {
      event.preventDefault();
      const orderId = printButton.dataset.orderId;
      openLabelWindow(orderId, printButton);
      return;
    }

    const requestPickupButton = event.target.closest(
      '[data-action="requestPickup"]'
    );
    if (requestPickupButton) {
      event.preventDefault();
      handlePickupRequest(requestPickupButton);
      return;
    }

    const viewPickupButton = event.target.closest('[data-action="viewPickup"]');
    if (viewPickupButton) {
      event.preventDefault();
      handleViewPickup(viewPickupButton);
      return;
    }

    const assignRiderButton = event.target.closest(
      '[data-action="assignRider"]'
    );
    if (assignRiderButton) {
      event.preventDefault();
      handleAssignRider(assignRiderButton);
    }
  });

  document.querySelectorAll(".order-card").forEach((card) => {
    togglePickupVisibility(card, card.dataset.pickupReady === "true");
  });
});

async function handlePickupRequest(button) {
  const card = button.closest(".order-card");
  const orderId = button.dataset.orderId;
  if (!card || !orderId) return;

  if (card.dataset.pickupReady === "false") {
    showOrderAlert(
      card,
      "Mark the order as 'To Ship' to request a pickup.",
      "info"
    );
    return;
  }

  button.disabled = true;
  showOrderAlert(card, "Scheduling pickup...", "info");

  try {
    const response = await fetch(`/seller/orders/${orderId}/pickup-request`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({}),
    });
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new Error(payload.error || "Unable to create pickup request.");
    }
    updatePickupSummary(card, payload.pickup, { orderId });
    showOrderAlert(card, "Pickup scheduled successfully.", "success");
  } catch (error) {
    showOrderAlert(card, error.message, "error");
  } finally {
    button.disabled = false;
  }
}

async function handleViewPickup(button) {
  const card = button.closest(".order-card");
  const orderId = button.dataset.orderId || card?.dataset.orderId;
  if (!card || !orderId) return;

  try {
    const pickup = await fetchPickupSummary(orderId);
    if (!pickup) {
      showOrderAlert(card, "No active pickup found for this order.", "info");
      return;
    }

    const pickupItem = (pickup.items || []).find(
      (item) => String(item.order_id) === String(orderId)
    );
    const pickupWindow = formatPickupWindow(pickup);
    const details = [
      `Pickup ${pickup.request_number || ""}`,
      `Status: ${formatPickupStatus(pickup.status)}`,
      pickupWindow,
      pickupItem ? `Packages: ${pickupItem.package_count || 1}` : null,
      pickup.rider_user_id
        ? `Rider: ${formatRiderLabel(pickup)}`
        : "Rider: Not assigned",
      pickup.rider_user_id
        ? null
        : "No available rider has accepted this pickup yet.",
    ]
      .filter(Boolean)
      .join(" · ");
    showOrderAlert(card, details, "info");
  } catch (error) {
    showOrderAlert(card, error.message, "error");
  }
}

async function handleAssignRider(button) {
  const card = button.closest(".order-card");
  const pickupId = button.dataset.pickupId;
  const orderId = card?.dataset.orderId;
  if (!card || !pickupId || !orderId) return;

  let pickupDetails;
  try {
    pickupDetails = await fetchPickupSummary(orderId);
  } catch (error) {
    showOrderAlert(card, error.message, "error");
    return;
  }

  if (!pickupDetails) {
    showOrderAlert(card, "No pickup found for this order.", "error");
    return;
  }

  updatePickupSummary(card, pickupDetails, { orderId });

  if (pickupDetails.rider_user_id) {
    const infoMessage = formatAssignedRiderAlert(pickupDetails);
    showOrderAlert(card, infoMessage, "info");
    const shouldContinue = window.confirm(
      `${infoMessage}\nAssign a different rider?`
    );
    if (!shouldContinue) {
      return;
    }
  } else {
    showOrderAlert(
      card,
      "No rider has accepted this pickup yet. You can assign one now.",
      "info"
    );
  }

  showOrderAlert(card, "Finding available riders...", "info");
  let riders;
  try {
    riders = await fetchEligibleRiders(pickupId);
  } catch (error) {
    showOrderAlert(card, error.message, "error");
    return;
  }

  if (!riders.length) {
    showOrderAlert(card, "No nearby riders are available right now.", "error");
    return;
  }

  const riderUserId = selectRiderCandidate(riders);
  if (!riderUserId) {
    showOrderAlert(card, "Rider assignment cancelled.", "info");
    return;
  }
  button.disabled = true;
  showOrderAlert(card, "Assigning rider...", "info");

  try {
    const response = await fetch(`/seller/pickups/${pickupId}/assign`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ rider_user_id: riderUserId }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new Error(payload.error || "Unable to assign rider.");
    }
    updatePickupSummary(card, payload.pickup, {
      orderId: card.dataset.orderId,
    });
    showOrderAlert(card, "Rider assigned successfully.", "success");
  } catch (error) {
    showOrderAlert(card, error.message, "error");
  } finally {
    button.disabled = false;
  }
}

async function handleStatusChange(event) {
  const select = event.target;
  const card = select.closest(".order-card");
  if (!card) return;

  const orderId = card.dataset.orderId;
  if (!orderId) return;

  const previousValue =
    select.dataset.currentValue || select.dataset.originalValue || select.value;
  const nextValue = select.value;

  if (previousValue === nextValue) {
    showOrderAlert(card, "Status unchanged.", "info");
    return;
  }

  select.disabled = true;
  card.classList.add("updating-status");
  showOrderAlert(
    card,
    `Updating status to ${STATUS_LABELS[nextValue] || nextValue}...`,
    "info"
  );

  try {
    const response = await fetch(`/seller/orders/${orderId}/status`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ status: nextValue }),
    });
    const payload = await response.json();

    if (!response.ok || !payload.success) {
      throw new Error(payload.error || "Unable to update order status.");
    }

    const resolvedStatus = payload.status || nextValue;
    const resolvedLabel =
      payload.status_label || STATUS_LABELS[resolvedStatus] || resolvedStatus;

    select.dataset.currentValue = resolvedStatus;
    select.value = resolvedStatus;
    card.dataset.status = resolvedStatus;
    const pickupReady = isShippingStatus(resolvedStatus);
    card.dataset.pickupReady = pickupReady ? "true" : "false";
    togglePickupVisibility(card, pickupReady);
    updateStatusBadge(card, resolvedStatus, resolvedLabel);
    updateStatusNote(card, payload.updated_at);
    updateStatDisplays(payload.stats);

    showOrderAlert(
      card,
      `Order marked as ${resolvedLabel}.`,
      payload.unchanged ? "info" : "success"
    );

    document.dispatchEvent(
      new CustomEvent("orderStatusUpdated", {
        detail: {
          orderId,
          status: resolvedStatus,
          stats: payload.stats,
        },
      })
    );
  } catch (error) {
    console.error("Failed to update order status", error);
    select.value = previousValue;
    showOrderAlert(card, error.message, "error");
  } finally {
    select.disabled = false;
    card.classList.remove("updating-status");
  }
}

function updateStatusBadge(card, statusValue, statusLabel) {
  const normalized = (statusValue || "").replace(/_/g, "-");
  const badge = card.querySelector(".status-badge");
  if (badge) {
    badge.className = `status-badge status-${normalized}`;
    badge.textContent =
      statusLabel || STATUS_LABELS[statusValue] || statusValue;
  }

  const dropdown = card.querySelector(".status-dropdown");
  if (dropdown) {
    dropdown.className = `status-dropdown status-${normalized}`;
    dropdown.dataset.currentValue = statusValue;
    dropdown.value = statusValue;
  }
}

function updateStatusNote(card, isoTimestamp) {
  const note = card.querySelector(".status-note");
  if (!note) return;
  note.textContent = `Updated ${formatTimestamp(isoTimestamp)}`;
}

function formatTimestamp(value) {
  if (!value) {
    return "just now";
  }

  const parsed = parseIsoDate(value);
  if (!parsed) {
    return "";
  }

  const now = new Date();
  const diffMs = Math.abs(now.getTime() - parsed.getTime());
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diffMs < minute) {
    return "just now";
  }
  if (diffMs < hour) {
    const minutes = Math.floor(diffMs / minute);
    return `${minutes}m ago`;
  }
  if (diffMs < day) {
    const hours = Math.floor(diffMs / hour);
    return `${hours}h ago`;
  }

  return parsed.toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function showOrderAlert(card, message, type = "info") {
  let alertNode = card.querySelector(".order-alert");
  if (!alertNode) {
    alertNode = document.createElement("div");
    alertNode.className = "order-alert";
    card.querySelector(".order-content")?.appendChild(alertNode);
  }

  alertNode.textContent = message;
  alertNode.classList.remove("success", "error", "info", "show");
  alertNode.classList.add(type, "show");

  if (alertNode._timer) {
    clearTimeout(alertNode._timer);
  }
  alertNode._timer = window.setTimeout(() => {
    alertNode.classList.remove("show");
  }, 4000);
}

function updateStatDisplays(stats) {
  if (!stats) return;
  Object.entries(stats).forEach(([key, value]) => {
    document.querySelectorAll(`[data-stat-key='${key}']`).forEach((node) => {
      node.textContent = value;
    });
    document.querySelectorAll(`[data-count-key='${key}']`).forEach((node) => {
      node.textContent = value;
    });
  });
}

function openLabelWindow(orderId, trigger) {
  if (!orderId) return;
  const card = trigger.closest(".order-card");
  const labelUrl = `/seller/orders/${orderId}/label`;
  const labelWindow = window.open(labelUrl, "_blank", "noopener");

  if (!labelWindow) {
    showOrderAlert(
      card,
      "Pop-up blocked. Please allow pop-ups to print the label.",
      "error"
    );
    return;
  }

  showOrderAlert(card, "Generating shipping label...", "info");
}

function updatePickupSummary(card, pickup, options = {}) {
  if (!card) return;
  const pickupBlock = card.querySelector("[data-pickup-summary]");
  if (!pickupBlock) return;

  const orderId = options.orderId || card.dataset.orderId;
  const statusValue = (pickup?.status || "").toLowerCase();
  const pickupItem = (pickup?.items || []).find(
    (item) => String(item.order_id) === String(orderId)
  );
  const packages = pickupItem?.package_count || pickup?.bulk_order_count || 1;
  card.dataset.pickupId = pickup?.id || "";
  card.dataset.pickupStatus = statusValue;
  card.dataset.riderName = pickup?.rider_name || "";
  card.dataset.riderPhone = pickup?.rider_phone || "";

  if (pickup) {
    const ordersMeta =
      pickup.bulk_order_count > 1 ? `· ${pickup.bulk_order_count} orders` : "";
    const riderMeta = pickup.rider_user_id
      ? `· Rider: ${formatRiderLabel(pickup)}`
      : "· Awaiting rider";

    pickupBlock.innerHTML = `
      <div class="pickup-chip status-${statusValue.replace(/_/g, "-")}">
        Pickup ${formatPickupStatus(pickup.status)}
      </div>
      <p class="pickup-meta">
        Ref: <span>${pickup.request_number || "—"}</span>
        ${ordersMeta}
      </p>
      <p class="pickup-meta">
        Packages: <span>${packages}</span>
        ${riderMeta}
      </p>
      <div class="pickup-actions-row">
        <button class="btn btn-accent" type="button" data-action="viewPickup" data-pickup-id="${
          pickup.id
        }" data-order-id="${orderId}">
          <i data-lucide="truck"></i>
          View pickup
        </button>
        <button class="btn btn-secondary" type="button" data-action="assignRider" data-pickup-id="${
          pickup.id
        }">
          <i data-lucide="user-check"></i>
          Assign rider
        </button>
      </div>
    `;
  } else {
    card.dataset.riderName = "";
    card.dataset.riderPhone = "";
    pickupBlock.innerHTML = `
      <div class="pickup-chip pickup-none">No pickup scheduled</div>
      <button class="btn btn-accent" type="button" data-action="requestPickup" data-order-id="${orderId}">
        <i data-lucide="truck"></i>
        Request pickup
      </button>
      <p class="pickup-helper">Move the order to \"To Ship\" to enable pickups.</p>
    `;
  }

  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }
  togglePickupVisibility(card, card.dataset.pickupReady === "true");
}

function formatPickupStatus(value) {
  if (!value) return "Not Scheduled";
  const normalized = value.toLowerCase();
  return (
    PICKUP_STATUS_LABELS[normalized] ||
    normalized.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase())
  );
}

window.updatePickupSummary = updatePickupSummary;
window.showOrderAlert = showOrderAlert;

async function fetchEligibleRiders(pickupId) {
  const response = await fetch(`/seller/pickups/${pickupId}/eligible-riders`, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  });
  const payload = await response.json();
  if (!response.ok || !payload.success) {
    throw new Error(payload.error || "Unable to load riders.");
  }
  return payload.riders || [];
}

async function fetchPickupSummary(orderId) {
  const response = await fetch(`/seller/orders/${orderId}/pickup-summary`, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  });
  const payload = await response.json();
  if (!response.ok || !payload.success) {
    throw new Error(payload.error || "Unable to load pickup details.");
  }
  return payload.pickup || null;
}

function selectRiderCandidate(riders) {
  if (!Array.isArray(riders) || riders.length === 0) {
    return null;
  }

  if (riders.length === 1) {
    const [candidate] = riders;
    const confirmSingle = window.confirm(
      `Assign ${candidate.name} (${
        candidate.match_reason || "Available"
      }) to this pickup?`
    );
    return confirmSingle ? candidate.user_id : null;
  }

  const menu = riders
    .map(
      (candidate, index) =>
        `${index + 1}. ${candidate.name} — ${
          candidate.match_reason || "Available"
        }`
    )
    .join("\n");

  const input = window.prompt(`Select a rider by number:\n${menu}`, "1");
  if (!input) return null;

  const selection = Number.parseInt(input, 10);
  if (Number.isNaN(selection) || selection < 1 || selection > riders.length) {
    window.alert("Invalid selection.");
    return null;
  }
  return riders[selection - 1].user_id;
}

function togglePickupVisibility(card, isShipping) {
  const pickupBlock = card.querySelector("[data-pickup-summary]");
  if (pickupBlock) {
    pickupBlock.hidden = !isShipping;
    pickupBlock.style.display = isShipping ? "" : "none";
    const helper = pickupBlock.querySelector(".pickup-helper");
    if (helper) {
      helper.style.display = isShipping ? "none" : "";
    }
  }

  const actionButtons = [
    card.querySelector('[data-action="printLabel"]'),
    card.querySelector('[data-action="contactBuyer"]'),
  ];
  actionButtons.forEach((button) => {
    if (button) {
      button.style.display = isShipping ? "none" : "";
    }
  });
}

function formatRiderLabel(pickup) {
  if (!pickup || !pickup.rider_user_id) {
    return "";
  }
  const label = pickup.rider_name || "Assigned rider";
  return pickup.rider_phone ? `${label} (${pickup.rider_phone})` : label;
}

function formatAssignedRiderAlert(pickup) {
  const label = formatRiderLabel(pickup);
  if (!label) {
    return "No rider is assigned to this pickup yet.";
  }
  return `Pickup already assigned to ${label}.`;
}

function isShippingStatus(value) {
  if (!value) return false;
  const normalized = String(value).toLowerCase();
  return (
    normalized === "shipping" ||
    normalized === "to ship" ||
    normalized === "to_ship"
  );
}

function formatPickupWindow(pickup) {
  if (!pickup) return "";
  const start = parseIsoDate(pickup.pickup_window_start);
  const end = parseIsoDate(pickup.pickup_window_end);
  const formatter = (date, withDate = true) =>
    date.toLocaleString(undefined, {
      month: "short",
      day: "2-digit",
      year: withDate ? "numeric" : undefined,
      hour: "2-digit",
      minute: "2-digit",
    });

  if (start && end) {
    const sameDay = start.toDateString() === end.toDateString();
    const dateLabel = sameDay ? formatter(start) : formatter(start);
    const endLabel = sameDay ? formatter(end, false) : formatter(end);
    const separator = sameDay ? " – " : " to ";
    return `Pickup window: ${dateLabel}${separator}${endLabel}`;
  }
  if (start) {
    return `Pickup window starts: ${formatter(start)}`;
  }
  if (end) {
    return `Pickup window ends: ${formatter(end)}`;
  }
  const requested = parseIsoDate(pickup.requested_at);
  return requested ? `Requested on ${formatter(requested)}` : "";
}

function parseIsoDate(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}
