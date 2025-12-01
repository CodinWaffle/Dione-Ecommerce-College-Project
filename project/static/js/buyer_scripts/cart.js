// Cart functionality
function addToCart(
  productId,
  productName,
  productPrice,
  selectedSize,
  selectedColor,
  selectedQuantity,
  metadata
) {
  const quantity = parseInt(selectedQuantity, 10) || 1;
  const payload = {
    product_id: productId,
    color: selectedColor,
    size: selectedSize,
    quantity,
  };

  // Optional metadata (variant id, size id, sku, etc.)
  if (metadata && typeof metadata === 'object') {
    if (metadata.variant_id || metadata.variantId) {
      payload.variant_id = metadata.variant_id || metadata.variantId;
    }
    if (metadata.size_id || metadata.sizeId) {
      payload.size_id = metadata.size_id || metadata.sizeId;
    }
    if (metadata.sku) {
      payload.sku = metadata.sku;
    }
  }

  fetch('/add-to-cart', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
    .then(response => response.json())
    .then(data => {
      if (!data || !data.success) {
        const errMsg = (data && (data.error || data.message)) || 'Failed to add item to cart';
        console.warn(errMsg, data);
        alert(errMsg);
        return;
      }

      if (typeof updateCartCount === 'function' && data.cart_count !== undefined) {
        updateCartCount(data.cart_count);
      } else if (data.cart_count !== undefined) {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
          cartCountElement.textContent = data.cart_count;
        }
      }

      const itemFromServer = data.item || {};
      const hydratedItem = {
        product_id: itemFromServer.product_id || productId,
        product_name: itemFromServer.product_name || productName,
        product_price: itemFromServer.product_price || productPrice,
        color: itemFromServer.color || selectedColor,
        size: itemFromServer.size || selectedSize,
        quantity: itemFromServer.quantity || quantity,
        variant_image: itemFromServer.variant_image || (metadata && metadata.image_url) || itemFromServer.image_url,
        sku: itemFromServer.sku || (metadata && metadata.sku),
      };

      window._lastCartPopupData = {
        color: hydratedItem.color,
        size: hydratedItem.size,
        quantity: hydratedItem.quantity,
        item: hydratedItem,
      };

      if (typeof updatePopupContent === 'function') {
        updatePopupContent(
          hydratedItem.color,
          hydratedItem.size,
          hydratedItem.quantity,
          hydratedItem
        );
      }

      if (typeof showCartSuccessAnimation === 'function') {
        showCartSuccessAnimation();
      } else if (typeof openCartModal === 'function') {
        openCartModal();
      }
    })
    .catch(error => {
      console.error('Error adding to cart:', error);
      alert('Error adding item to cart. Please try again.');
    });
}

// Navigation to cart page
function goToCart() {
  window.location.href = "/buyer/cart";
}

// Update cart count in header
function updateCartCount(count) {
  const cartCountElement = document.querySelector(".cart-count");
  if (cartCountElement) {
    cartCountElement.textContent = count;
  }
}

// Add to bag functionality that integrates with add to cart popup
function addToBag(
  productId,
  productName,
  productPrice,
  selectedSize,
  selectedColor,
  selectedQuantity,
  metadata
) {
  // Add item to cart
  addToCart(
    productId,
    productName,
    productPrice,
    selectedSize,
    selectedColor,
    selectedQuantity,
    metadata
  );

  // Update cart count (you can get this from server or local storage)
  const currentCount =
    parseInt(document.querySelector(".cart-count").textContent) || 0;
  updateCartCount(currentCount + parseInt(selectedQuantity));
}

// Saved items functionality
function saveForLater(itemId) {
  // This function can be overridden in specific pages
  console.log("Save for later:", itemId);
}

function moveToCart(itemId) {
  // This function can be overridden in specific pages
  console.log("Move to cart:", itemId);
}

function removeSavedItem(itemId) {
  // This function can be overridden in specific pages
  console.log("Remove saved item:", itemId);
}

// Remove cart item (called from cart.html remove button)
function removeItem(itemId) {
  if (!itemId) return;
  if (!confirm("Remove this item from your cart?")) return;

  fetch("/remove-from-cart", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item_id: itemId }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data && data.success) {
        // Remove element from DOM
        const el = document.querySelector(
          `.product-card[data-item-id="${itemId}"]`
        );
        if (el && el.parentNode) el.parentNode.removeChild(el);

        // Update header cart count if provided
        if (
          typeof updateCartCount === "function" &&
          data.cart_count !== undefined
        ) {
          updateCartCount(data.cart_count);
        } else if (data.cart_count !== undefined) {
          const headerCount = document.querySelector(".cart-count");
          if (headerCount) headerCount.textContent = data.cart_count;
        }

        // Update order summary subtotal if provided
        if (data.subtotal !== undefined) {
          const subtotalEl = document.getElementById("subtotal");
          if (subtotalEl)
            subtotalEl.textContent = `₱${parseFloat(data.subtotal).toFixed(2)}`;
        } else {
          // Fallback: reload to ensure accurate totals
          window.location.reload();
        }

        // If no more product cards remain, reload to show empty cart state
        const remaining = document.querySelectorAll(".product-card").length;
        if (remaining === 0) window.location.reload();
      } else {
        alert((data && data.error) || "Failed to remove item");
        console.warn("Remove failed", data);
      }
    })
    .catch((err) => {
      console.error("Error removing cart item:", err);
      alert("Error removing item from cart");
    });
}

// Initialize cart functionality when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Add event listener for cart button in header
  const cartBtn = document.querySelector(".cart-btn");
  if (cartBtn) {
    cartBtn.addEventListener("click", function (e) {
      e.preventDefault();
      goToCart();
    });
  }

  // Add event listener for View Bag button in popup
  const viewBagBtn = document.querySelector(".cart-checkout-button");
  if (viewBagBtn) {
    viewBagBtn.addEventListener("click", function (e) {
      e.preventDefault();
      goToCart();
    });
  }
});
