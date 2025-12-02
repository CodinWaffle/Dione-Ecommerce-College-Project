document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  const bootstrapNode = document.getElementById("cart-page-bootstrap");
  const bootstrapData = bootstrapNode
    ? JSON.parse(bootstrapNode.textContent || "{}")
    : {};

  const cartItems = (bootstrapData.cartItems || []).map((item) => ({
    ...item,
    selected: item.selected !== false,
  }));
  const savedItems = bootstrapData.savedItems || [];
  const checkoutUrl = bootstrapData.checkoutUrl || "/checkout";
  const DEFAULT_MAX_QTY = Number(bootstrapData.maxQuantity || 100);
  const currency = new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    minimumFractionDigits: 2,
  });

  function getMaxQuantity(item) {
    if (!item) {
      return DEFAULT_MAX_QTY;
    }
    return Number(item.max_quantity ?? item.maxQuantity ?? DEFAULT_MAX_QTY);
  }

  function findItem(id, source) {
    return source.find((item) => `${item.id}` === `${id}`);
  }

  function removeFromDOM(itemId, className) {
    const el = document.querySelector(`[data-item-id="${itemId}"]`);
    if (!el) {
      return;
    }

    el.classList.add(className);
    setTimeout(() => el.remove(), 300);
  }

  function setCardSelectionState(itemId, isSelected) {
    const card = document.querySelector(`[data-item-id="${itemId}"]`);
    if (!card) return;
    card.classList.toggle("unselected", !isSelected);
    const checkbox = card.querySelector(".cart-select");
    if (checkbox) {
      checkbox.checked = !!isSelected;
    }
  }

  function notification(message, type = "info") {
    const node = document.createElement("div");
    node.className = `notification notification-${type}`;
    node.innerHTML = `
      <div class="notification-content">
        <i data-lucide="${
          type === "success"
            ? "check-circle"
            : type === "error"
            ? "x-circle"
            : "info"
        }"></i>
        <span>${message}</span>
      </div>
    `;
    document.body.appendChild(node);
    lucide?.createIcons();
    requestAnimationFrame(() => node.classList.add("show"));
    setTimeout(() => {
      node.classList.remove("show");
      setTimeout(() => node.remove(), 300);
    }, 3000);
  }

  function updateBadges() {
    const totalItems = cartItems.reduce(
      (sum, item) => sum + (item.quantity || 0),
      0
    );
    const uniqueItems = cartItems.length;
    const selectedCount = cartItems.filter((item) => item.selected).length;

    const itemNumber = document.querySelector(".item-number");
    const itemText = document.querySelector(".item-text");
    if (itemNumber) itemNumber.textContent = totalItems;
    if (itemText) itemText.textContent = `item${totalItems === 1 ? "" : "s"}`;

    const cartBadge = document.querySelector(".cart-badge");
    if (cartBadge) cartBadge.textContent = uniqueItems;

    const summaryBadge = document.querySelector(".summary-badge");
    if (summaryBadge)
      summaryBadge.textContent = `${uniqueItems} item${
        uniqueItems === 1 ? "" : "s"
      }`;

    const selectedBadge = document.getElementById("selected-summary-count");
    if (selectedBadge) {
      selectedBadge.textContent = `${selectedCount} selected`;
    }

    const selectedLabel = document.getElementById("selected-count-label");
    if (selectedLabel) {
      selectedLabel.textContent = `${selectedCount} selected`;
    }

    const selectAll = document.getElementById("select-all-checkbox");
    if (selectAll) {
      selectAll.checked = selectedCount === uniqueItems && uniqueItems > 0;
      selectAll.indeterminate =
        selectedCount > 0 && selectedCount < uniqueItems;
    }
  }

  function updateSummary() {
    const subtotal = cartItems.reduce(
      (sum, item) =>
        sum +
        (item.selected ? Number(item.price) * Number(item.quantity || 1) : 0),
      0
    );
    const deliveryFee = subtotal >= 1500 || subtotal === 0 ? 0 : 150;
    const discount = 0;
    const total = subtotal + deliveryFee - discount;

    const subtotalEl = document.getElementById("subtotal");
    const deliveryEl = document.getElementById("delivery");
    const totalEl = document.getElementById("total");

    if (subtotalEl) subtotalEl.textContent = currency.format(subtotal);
    if (deliveryEl) {
      deliveryEl.innerHTML =
        deliveryFee === 0
          ? '<span class="free-shipping">FREE</span>'
          : currency.format(deliveryFee);
    }
    if (totalEl) totalEl.textContent = currency.format(total);
  }

  function persistAndRefresh() {
    updateBadges();
    updateSummary();
    if (!cartItems.length) {
      window.location.reload();
    }
  }

  function toggleSelection(itemId, explicitValue) {
    const item = findItem(itemId, cartItems);
    if (!item) return;
    const nextState =
      typeof explicitValue === "boolean" ? explicitValue : !item.selected;
    item.selected = nextState;
    setCardSelectionState(itemId, nextState);
    persistAndRefresh();
  }

  function selectAllItems(isChecked) {
    cartItems.forEach((item) => {
      item.selected = isChecked;
      setCardSelectionState(item.id, isChecked);
    });
    persistAndRefresh();
  }

  function goToCheckout() {
    const selectedItems = cartItems.filter((item) => item.selected);
    if (!selectedItems.length) {
      notification("Please select at least one item to proceed.", "info");
      return;
    }

    // Send selected item IDs to backend
    fetch("/set-checkout-items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        selected_item_ids: selectedItems.map((item) => item.id),
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          window.location.href = checkoutUrl;
        } else {
          notification("Failed to proceed to checkout", "error");
        }
      })
      .catch((error) => {
        console.error("Error setting checkout items:", error);
        notification("Failed to proceed to checkout", "error");
      });
  }

  function syncQuantity(itemId, quantity) {
    return fetch("/update-cart-quantity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: itemId, quantity }),
    }).then((res) => res.json());
  }

  window.updateQuantity = function updateQuantity(itemId, delta) {
    const item = findItem(itemId, cartItems);
    if (!item) return;

    const maxAllowed = getMaxQuantity(item);
    const proposed = Number(item.quantity || 1) + delta;
    const newQty = Math.max(1, Math.min(maxAllowed, proposed));

    if (newQty === item.quantity && delta > 0 && proposed > maxAllowed) {
      notification(`Maximum of ${maxAllowed} per item.`, "info");
      return;
    }

    if (newQty === item.quantity && delta < 0) {
      return;
    }
    item.quantity = newQty;

    const qtyInput = document.getElementById(`qty-${itemId}`);
    if (qtyInput) {
      qtyInput.value = newQty;
      qtyInput.max = maxAllowed;
    }

    const priceNode = document.querySelector(
      `[data-item-id="${itemId}"] .product-price`
    );
    if (priceNode)
      priceNode.textContent = currency.format(Number(item.price) * newQty);

    const unitPriceNode = document.querySelector(
      `[data-item-id="${itemId}"] .unit-price`
    );
    if (unitPriceNode) {
      if (newQty > 1) {
        unitPriceNode.textContent = `${currency.format(
          Number(item.price)
        )} each`;
        unitPriceNode.style.display = "block";
      } else {
        unitPriceNode.style.display = "none";
      }
    }

    const card = document.querySelector(`[data-item-id="${itemId}"]`);
    card?.classList.add("updating");
    setTimeout(() => card?.classList.remove("updating"), 300);

    syncQuantity(itemId, newQty)
      .then((data) => {
        if (!data?.success) {
          throw new Error(data?.error || "Failed to update quantity");
        }
        persistAndRefresh();
      })
      .catch((err) => {
        console.error("Error updating quantity:", err);
        notification("Could not update quantity. Please try again.", "error");
      });
  };

  window.removeItem = function removeItem(itemId) {
    const item = findItem(itemId, cartItems);
    if (!item || !confirm(`Remove "${item.name}" from your cart?`)) return;

    fetch("/remove-from-cart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: itemId }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data?.success) {
          throw new Error(data?.error || "Failed to remove item");
        }

        cartItems.splice(cartItems.indexOf(item), 1);
        removeFromDOM(itemId, "removing");
        persistAndRefresh();

        if (typeof updateCartCount === "function") {
          updateCartCount(cartItems.length);
        } else {
          const headerCount = document.querySelector(".cart-count");
          if (headerCount) headerCount.textContent = cartItems.length;
        }
      })
      .catch((err) => {
        console.error("Error removing cart item:", err);
        notification("Failed to remove item. Please try again.", "error");
      });
  };

  window.saveForLater = function saveForLater(itemId) {
    const item = findItem(itemId, cartItems);
    if (!item) return;

    savedItems.push(item);
    cartItems.splice(cartItems.indexOf(item), 1);
    removeFromDOM(itemId, "saving");
    notification(`"${item.name}" saved for later`, "success");
    persistAndRefresh();
  };

  document.addEventListener("click", (event) => {
    const selectBox = event.target.closest(".cart-select");
    if (selectBox) {
      toggleSelection(selectBox.dataset.itemId, selectBox.checked);
      return;
    }

    const actionBtn = event.target.closest("[data-cart-action]");
    if (!actionBtn) {
      return;
    }

    const { cartAction: action, itemId } = actionBtn.dataset;
    switch (action) {
      case "remove":
        removeItem(itemId);
        break;
      case "increase":
        updateQuantity(itemId, 1);
        break;
      case "decrease":
        updateQuantity(itemId, -1);
        break;
      case "save":
        saveForLater(itemId);
        break;
      case "edit":
        notification("Edit functionality coming soon!", "info");
        break;
      case "apply-promo":
        applyPromoCode();
        break;
      case "checkout":
        goToCheckout();
        break;
      default:
        break;
    }
  });

  const selectAllCheckbox = document.getElementById("select-all-checkbox");
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener("change", (e) => {
      selectAllItems(e.target.checked);
    });
  }

  cartItems.forEach((item) => {
    const initialState = item.selected !== false;
    item.selected = initialState;
    setCardSelectionState(item.id, initialState);
  });

  updateBadges();
  updateSummary();
});
