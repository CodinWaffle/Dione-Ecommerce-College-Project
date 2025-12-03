// Pickup Management Page JS

document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("pickupTableBody");

  tableBody?.addEventListener("click", async (event) => {
    const acceptButton = event.target.closest(".accept-pickup-btn");
    if (acceptButton) {
      event.preventDefault();
      await handlePickupAccept(acceptButton);
      return;
    }

    const completeButton = event.target.closest(".mark-picked-up-btn");
    if (completeButton) {
      event.preventDefault();
      await handlePickupComplete(completeButton);
    }
  });
});

async function handlePickupAccept(button) {
  const row = button.closest("tr");
  const pickupId = row?.dataset.pickupId;
  if (!pickupId) return;

  button.disabled = true;
  try {
    const response = await fetch(`/rider/api/pickups/${pickupId}/accept`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
    });
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new Error(payload.error || "Unable to accept pickup.");
    }
    updatePickupRow(row, payload.pickup);
  } catch (error) {
    window.alert(error.message);
  } finally {
    button.disabled = false;
  }
}

async function handlePickupComplete(button) {
  const row = button.closest("tr");
  const pickupId = row?.dataset.pickupId;
  if (!pickupId) return;

  if (!row || row.dataset.assigned !== "1") {
    window.alert("Accept this pickup before marking it as completed.");
    return;
  }

  button.disabled = true;
  try {
    const response = await fetch(`/rider/api/pickups/${pickupId}/complete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ mark_complete: true }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new Error(payload.error || "Unable to mark pickup as completed.");
    }
    updatePickupRow(row, payload.pickup);
  } catch (error) {
    window.alert(error.message);
  } finally {
    button.disabled = false;
  }
}

function updatePickupRow(row, pickup) {
  if (!row || !pickup) return;
  row.dataset.rawStatus = pickup.raw_status;
  row.dataset.assigned = pickup.assigned_to_me ? "1" : "0";

  const itemsCell = row.querySelector(".pickup-items-cell");
  renderPickupItems(itemsCell, pickup);

  const statusBadge = row.querySelector(".pickup-status-badge");
  if (statusBadge) {
    statusBadge.textContent = pickup.status;
    statusBadge.className = `status-badge pickup-status-badge status-${pickup.status
      .toLowerCase()
      .replace(/\s+/g, "-")}`;
  }

  const acceptButton = row.querySelector(".accept-pickup-btn");
  if (acceptButton) {
    acceptButton.style.display =
      pickup.raw_status === "pending" && !pickup.assigned_to_me ? "" : "none";
  }

  const completeButton = row.querySelector(".mark-picked-up-btn");
  if (completeButton) {
    const canComplete =
      pickup.raw_status === "pending" || pickup.raw_status === "assigned";
    completeButton.disabled = !pickup.assigned_to_me;
    completeButton.style.display = canComplete ? "" : "none";
  }

  const viewProofButton = row.querySelector(".view-proof-btn");
  if (viewProofButton) {
    viewProofButton.style.display =
      pickup.raw_status === "picked_up" || pickup.raw_status === "completed"
        ? ""
        : "none";
  } else if (
    pickup.raw_status === "picked_up" ||
    pickup.raw_status === "completed"
  ) {
    const actionCell = row.querySelector("td:last-child");
    if (actionCell) {
      actionCell.insertAdjacentHTML(
        "beforeend",
        `
          <button class="action-btn view-proof-btn" title="View Proof">
            <span class="material-symbols-outlined">visibility</span>
          </button>
        `
      );
    }
  }
}

function renderPickupItems(cell, pickup) {
  if (!cell || !pickup) return;

  const names = Array.isArray(pickup.item_names) ? pickup.item_names : [];
  cell.innerHTML = "";

  if (names.length) {
    const primary = document.createElement("div");
    primary.className = "pickup-item-name";
    primary.textContent = names[0];
    cell.appendChild(primary);

    if (names.length > 1) {
      const extra = document.createElement("div");
      extra.className = "pickup-item-extra";
      extra.textContent = `+${names.length - 1} more`;
      cell.appendChild(extra);
    }
    return;
  }

  if (typeof pickup.items === "number") {
    const label = pickup.items === 1 ? "item" : "items";
    cell.textContent = `${pickup.items} ${label}`;
  } else if (pickup.item_summary) {
    cell.textContent = pickup.item_summary;
  } else {
    cell.textContent = "—";
  }
}
