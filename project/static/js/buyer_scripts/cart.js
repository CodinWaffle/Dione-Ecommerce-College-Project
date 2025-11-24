// Cart functionality
function addToCart(productId, productName, productPrice, selectedSize, selectedColor, selectedQuantity) {
    // Add item to cart logic here
    console.log('Add to cart:', {
        id: productId,
        name: productName,
        price: productPrice,
        size: selectedSize,
        color: selectedColor,
        quantity: selectedQuantity
    });
    
    // Send to backend (optional - you can implement this later)
    fetch('/api/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            product_name: productName,
            product_price: productPrice,
            selected_size: selectedSize,
            selected_color: selectedColor,
            selected_quantity: selectedQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Successfully added to cart');
            // Update cart count if needed
            if (data.cart_count) {
                updateCartCount(data.cart_count);
            }
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
    });
    
    // Show success animation and modal (this will happen regardless of backend call)
    if (typeof showCartSuccessAnimation === 'function') {
        showCartSuccessAnimation();
    }
}

// Navigation to cart page
function goToCart() {
    window.location.href = '/buyer/cart';
}

// Update cart count in header
function updateCartCount(count) {
    const cartCountElement = document.querySelector('.cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
    }
}

// Add to bag functionality that integrates with add to cart popup
function addToBag(productId, productName, productPrice, selectedSize, selectedColor, selectedQuantity) {
    // Add item to cart
    addToCart(productId, productName, productPrice, selectedSize, selectedColor, selectedQuantity);
    
    // Update cart count (you can get this from server or local storage)
    const currentCount = parseInt(document.querySelector('.cart-count').textContent) || 0;
    updateCartCount(currentCount + parseInt(selectedQuantity));
}

// Saved items functionality
function saveForLater(itemId) {
    // This function can be overridden in specific pages
    console.log('Save for later:', itemId);
}

function moveToCart(itemId) {
    // This function can be overridden in specific pages
    console.log('Move to cart:', itemId);
}

function removeSavedItem(itemId) {
    // This function can be overridden in specific pages
    console.log('Remove saved item:', itemId);
}

// Initialize cart functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for cart button in header
    const cartBtn = document.querySelector('.cart-btn');
    if (cartBtn) {
        cartBtn.addEventListener('click', function(e) {
            e.preventDefault();
            goToCart();
        });
    }
    
    // Add event listener for View Bag button in popup
    const viewBagBtn = document.querySelector('.cart-checkout-button');
    if (viewBagBtn) {
        viewBagBtn.addEventListener('click', function(e) {
            e.preventDefault();
            goToCart();
        });
    }
});
