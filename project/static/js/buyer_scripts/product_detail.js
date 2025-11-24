// Global variables
let currentImageIndex = 0
const totalImages = 3

// Image switching functionality
function changeMainImage(thumbnail, index) {
  const mainImage = document.getElementById("mainImage")
  const thumbnails = document.querySelectorAll(".thumbnail")

  // Update main image
  mainImage.src = thumbnail.src

  // Update active thumbnail
  thumbnails.forEach((thumb) => thumb.classList.remove("active"))
  thumbnail.classList.add("active")

  // Update current index
  currentImageIndex = index
}

document.addEventListener("DOMContentLoaded", () => {
  // Initialize stock display and availability
  updateSizeAvailability();
  updateColorAvailability();
  updateStockDisplay();
  
  // Initialize quantity buttons
  updateQuantityButtons();
  
  // Add event listeners to quantity buttons (in case onclick doesn't work)
  const decreaseBtn = document.getElementById('decreaseBtn');
  const increaseBtn = document.getElementById('increaseBtn');
  const quantityInput = document.getElementById('quantityInput');
  
  if (decreaseBtn) {
    decreaseBtn.addEventListener('click', decreaseQuantity);
  }
  
  if (increaseBtn) {
    increaseBtn.addEventListener('click', increaseQuantity);
  }
  
  if (quantityInput) {
    quantityInput.addEventListener('input', updateQuantity);
    quantityInput.addEventListener('change', updateQuantity);
  }
})

// Global variables for stock management
let currentSelectedColor = 'Black';
let currentSelectedSize = 'XS';

// Update stock display
function updateStockDisplay() {
  const stockIndicator = document.getElementById('stockIndicator');
  const activeColorBtn = document.querySelector('.color-option.active');
  const activeSizeBtn = document.querySelector('.size-option.active');
  
  if (activeColorBtn && activeSizeBtn) {
    const colorStock = JSON.parse(activeColorBtn.dataset.stock);
    const selectedSize = activeSizeBtn.dataset.size;
    const stock = colorStock[selectedSize];
    
    stockIndicator.textContent = stock > 0 ? stock : '0';
    
    // Update stock indicator styling
    stockIndicator.className = 'stock-indicator';
    if (stock === 0) {
      stockIndicator.classList.add('out-of-stock');
    } else if (stock <= 3) {
      stockIndicator.classList.add('low-stock');
    } else {
      stockIndicator.classList.add('in-stock');
    }
    
    // Update add to bag button
    const addToBagBtn = document.querySelector('.add-to-bag-btn');
    if (stock === 0) {
      addToBagBtn.disabled = true;
      addToBagBtn.textContent = 'OUT OF STOCK';
      addToBagBtn.style.opacity = '0.5';
      addToBagBtn.style.cursor = 'not-allowed';
    } else {
      addToBagBtn.disabled = false;
      addToBagBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <path d="M16 10a4 4 0 0 1-8 0"></path>
        </svg>
        ADD TO BAG
      `;
      addToBagBtn.style.opacity = '1';
      addToBagBtn.style.cursor = 'pointer';
    }
    
    // Update quantity buttons when stock changes
    updateQuantityButtons();
  }
}

// Update size availability based on color
function updateSizeAvailability() {
  const activeColorBtn = document.querySelector('.color-option.active');
  const sizeOptions = document.querySelectorAll('.size-option');
  
  if (activeColorBtn) {
    const colorStock = JSON.parse(activeColorBtn.dataset.stock);
    
    sizeOptions.forEach(sizeBtn => {
      const size = sizeBtn.dataset.size;
      const stock = colorStock[size];
      
      if (stock === 0) {
        sizeBtn.classList.add('disabled');
        sizeBtn.onclick = null;
      } else {
        sizeBtn.classList.remove('disabled');
        sizeBtn.onclick = () => selectSize(sizeBtn);
      }
    });
  }
}

// Update color availability based on size
function updateColorAvailability() {
  const activeSizeBtn = document.querySelector('.size-option.active');
  const colorOptions = document.querySelectorAll('.color-option');
  
  if (activeSizeBtn) {
    const selectedSize = activeSizeBtn.dataset.size;
    
    colorOptions.forEach(colorBtn => {
      const colorStock = JSON.parse(colorBtn.dataset.stock);
      const stock = colorStock[selectedSize];
      
      if (stock === 0) {
        colorBtn.classList.add('disabled');
        colorBtn.onclick = null;
      } else {
        colorBtn.classList.remove('disabled');
        colorBtn.onclick = () => selectColor(colorBtn);
      }
    });
  }
}

// Color selection
function selectColor(colorBtn) {
  // Don't allow selection of disabled colors
  if (colorBtn.classList.contains('disabled')) {
    return;
  }
  
  const colorOptions = document.querySelectorAll(".color-option")
  const selectedColorSpan = document.querySelector(".selected-color")

  colorOptions.forEach((option) => option.classList.remove("active"))
  colorBtn.classList.add("active")

  selectedColorSpan.textContent = colorBtn.dataset.color
  currentSelectedColor = colorBtn.dataset.color;
  
  // Update size availability and stock display
  updateSizeAvailability();
  updateStockDisplay();
}

// Size selection
function selectSize(sizeBtn) {
  // Don't allow selection of disabled sizes
  if (sizeBtn.classList.contains('disabled')) {
    return;
  }
  
  const sizeOptions = document.querySelectorAll(".size-option")

  sizeOptions.forEach((option) => option.classList.remove("active"))
  sizeBtn.classList.add("active")
  
  currentSelectedSize = sizeBtn.dataset.size;
  
  // Update color availability and stock display
  updateColorAvailability();
  updateStockDisplay();
}

// Wishlist toggle
document.getElementById("wishlistBtn").addEventListener("click", function () {
  this.classList.toggle("active")
})

// Add to bag functionality
function addToBag() {
  const selectedColor = document.querySelector(".color-option.active").dataset.color
  const selectedSize = document.querySelector(".size-option.active").textContent
  const selectedQuantity = document.getElementById("quantityInput").value
  
  // Get product details from the page
  const productName = document.querySelector('.product-title').textContent;
  const productPrice = parseFloat(document.querySelector('.price').textContent.replace('$', ''));
  const productId = document.querySelector('[data-product-id]')?.dataset.productId || Math.floor(Math.random() * 10000);

  // Update the popup with selected options
  updatePopupContent(selectedColor, selectedSize, selectedQuantity)

  // Add to cart using the cart.js function
  if (typeof addToCart === 'function') {
    addToCart(productId, productName, productPrice, selectedSize, selectedColor, selectedQuantity);
  }

  // Show success animation first, then modal
  showCartSuccessAnimation()
}

// Function to update popup content dynamically
function updatePopupContent(color, size, quantity) {
  // Update size
  const modalSelectedSize = document.getElementById('cartModalSelectedSize')
  if (modalSelectedSize) {
    modalSelectedSize.textContent = size
  }
  
  // Update color
  const modalSelectedColor = document.getElementById('cartModalSelectedColor')
  if (modalSelectedColor) {
    modalSelectedColor.textContent = color
  }
  
  // Update quantity
  const modalSelectedQuantity = document.getElementById('cartModalSelectedQuantity')
  if (modalSelectedQuantity) {
    modalSelectedQuantity.textContent = quantity
  }
  
  // Update product name to include color if needed
  const productNameElement = document.querySelector('.cart-modal .cart-product-name')
  if (productNameElement && color) {
    const baseName = productNameElement.textContent.split(' in ')[0] // Remove existing color info
    productNameElement.textContent = `${baseName} in ${color}`
  }
  
  // Update item count in header
  const itemCount = document.querySelector('.cart-item-count')
  if (itemCount) {
    const itemText = parseInt(quantity) === 1 ? 'Item' : 'Items'
    itemCount.textContent = `${quantity} ${itemText}`
  }
}

// Expandable sections
function toggleSection(header) {
  const content = header.nextElementSibling
  const isActive = header.classList.contains("active")

  // Close all sections
  document.querySelectorAll(".section-header").forEach((h) => {
    h.classList.remove("active")
    h.nextElementSibling.classList.remove("active")
  })

  // Open clicked section if it wasn't active
  if (!isActive) {
    header.classList.add("active")
    content.classList.add("active")
  }
}

// Bottom tabs functionality
function switchTab(tabBtn, tabId) {
  const tabBtns = document.querySelectorAll(".tab-btn")
  const tabPanels = document.querySelectorAll(".tab-panel")

  tabBtns.forEach((btn) => btn.classList.remove("active"))
  tabPanels.forEach((panel) => panel.classList.remove("active"))

  tabBtn.classList.add("active")
  document.getElementById(tabId).classList.add("active")
}

// Breadcrumb navigation functions
function navigateToHome(event) {
  event.preventDefault()
  // Navigate to home page
  window.location.href = '/'
}

function navigateToCategory(event, category) {
  event.preventDefault()
  // Navigate to category page
  window.location.href = `/category/${category}`
}

// Quantity management functions
function updateQuantityButtons() {
  const quantityInput = document.getElementById('quantityInput');
  const decreaseBtn = document.getElementById('decreaseBtn');
  const increaseBtn = document.getElementById('increaseBtn');
  const stockIndicator = document.getElementById('stockIndicator');
  
  const currentQuantity = parseInt(quantityInput.value) || 1;
  const availableStock = parseInt(stockIndicator.textContent) || 0;
  
  // Disable decrease button if quantity is 1
  decreaseBtn.disabled = currentQuantity <= 1;
  
  // Disable increase button if quantity equals available stock
  increaseBtn.disabled = currentQuantity >= availableStock || availableStock === 0;
  
  // Update max attribute of input
  quantityInput.max = availableStock;
  
  // Ensure quantity is within valid range
  if (currentQuantity > availableStock && availableStock > 0) {
    quantityInput.value = availableStock;
  } else if (currentQuantity < 1) {
    quantityInput.value = 1;
  }
}

function increaseQuantity() {
  const quantityInput = document.getElementById('quantityInput');
  const stockIndicator = document.getElementById('stockIndicator');
  
  const currentQuantity = parseInt(quantityInput.value) || 1;
  const availableStock = parseInt(stockIndicator.textContent) || 0;
  
  if (currentQuantity < availableStock) {
    quantityInput.value = currentQuantity + 1;
    updateQuantityButtons();
  }
}

function decreaseQuantity() {
  const quantityInput = document.getElementById('quantityInput');
  const currentQuantity = parseInt(quantityInput.value) || 1;
  
  if (currentQuantity > 1) {
    quantityInput.value = currentQuantity - 1;
    updateQuantityButtons();
  }
}

function updateQuantity() {
  const quantityInput = document.getElementById('quantityInput');
  const stockIndicator = document.getElementById('stockIndicator');
  const availableStock = parseInt(stockIndicator.textContent) || 0;
  
  let quantity = parseInt(quantityInput.value) || 1;
  
  // Ensure quantity is within bounds
  if (quantity < 1) {
    quantity = 1;
  } else if (quantity > availableStock && availableStock > 0) {
    quantity = availableStock;
  }
  
  quantityInput.value = quantity;
  updateQuantityButtons();
}

// Report product functionality
function reportProduct() {
  // Show a simple confirmation dialog
  const reasons = [
    'Inappropriate content',
    'Misleading information',
    'Copyright violation',
    'Counterfeit product',
    'Other'
  ];
  
  let message = 'Why are you reporting this product?\n\n';
  reasons.forEach((reason, index) => {
    message += `${index + 1}. ${reason}\n`;
  });
  
  const choice = prompt(message + '\nEnter the number (1-5):');
  
  if (choice && choice >= 1 && choice <= 5) {
    const selectedReason = reasons[choice - 1];
    alert(`Thank you for your report. We will review this product for: ${selectedReason}`);
    
    // Here you would typically send the report to your backend
    console.log('Product reported for:', selectedReason);
  }
}

// Size guide scroll functionality
function scrollToSizeGuide(event) {
  event.preventDefault();
  
  // First, switch to the Product Details tab if not already active
  const productDetailsTab = document.querySelector('.tab-btn[onclick*="product-details"]');
  if (productDetailsTab && !productDetailsTab.classList.contains('active')) {
    switchTab(productDetailsTab, 'product-details');
  }
  
  // Wait a moment for tab switch animation, then scroll
  setTimeout(() => {
    const sizeGuideSection = document.querySelector('.size-guide');
    if (sizeGuideSection) {
      sizeGuideSection.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
      
      // Add a subtle highlight effect
      sizeGuideSection.style.transition = 'background-color 0.3s ease';
      sizeGuideSection.style.backgroundColor = 'rgba(142, 68, 173, 0.05)';
      
      setTimeout(() => {
        sizeGuideSection.style.backgroundColor = 'transparent';
      }, 2000);
    }
  }, 100);
}

// Zoom box functionality
function showZoomBox(event) {
  const zoomBox = document.getElementById('zoomBox');
  const zoomViewer = document.getElementById('zoomViewer');
  const zoomImage = document.getElementById('zoomImage');
  const mainImage = event.currentTarget;
  const mainImg = mainImage.querySelector('img');
  const rect = mainImage.getBoundingClientRect();
  
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  
  // Position zoom box
  let boxX = x - 75;
  let boxY = y - 75;
  
  // Keep zoom box within image bounds
  boxX = Math.max(0, Math.min(boxX, rect.width - 150));
  boxY = Math.max(0, Math.min(boxY, rect.height - 150));
  
  zoomBox.style.display = 'block';
  zoomBox.style.left = boxX + 'px';
  zoomBox.style.top = boxY + 'px';
  
  // Show zoom viewer
  zoomViewer.style.display = 'block';
  
  // Calculate the percentage position of the zoom box center
  const percentX = (boxX + 75) / rect.width;
  const percentY = (boxY + 75) / rect.height;
  
  // Position the zoomed image (8x magnification for extreme fabric detail viewing)
  const zoomImageX = -(percentX * zoomImage.offsetWidth - 175);
  const zoomImageY = -(percentY * zoomImage.offsetHeight - 175);
  
  zoomImage.style.transform = `translate(${zoomImageX}px, ${zoomImageY}px)`;
}

function hideZoomBox() {
  const zoomBox = document.getElementById('zoomBox');
  const zoomViewer = document.getElementById('zoomViewer');
  zoomBox.style.display = 'none';
  zoomViewer.style.display = 'none';
}