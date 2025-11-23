// Get the modal
const productDetailsModal = document.getElementById("productDetailsModal");
const closeDetailsBtn = document.querySelector(".close-details");

// Get content containers
const basicDetailsContent = document.getElementById("basicDetailsContent");
const productImagesContent = document.getElementById("productImagesContent");
const descriptionContent = document.getElementById("descriptionContent");
const stockDetailsContent = document.getElementById("stockDetailsContent");

// Close modal when clicking the close button
closeDetailsBtn.addEventListener("click", () => {
  productDetailsModal.style.display = "none";
});

// Close modal when clicking outside
window.addEventListener("click", (event) => {
  if (event.target === productDetailsModal) {
    productDetailsModal.style.display = "none";
  }
});

function showProductDetails(productId) {
  // Get product data from localStorage
  const products = JSON.parse(localStorage.getItem("products")) || [];
  const product = products.find((p) => p.id === productId);

  if (!product) {
    console.error("Product not found");
    return;
  }

  // Populate basic details
  basicDetailsContent.innerHTML = `
        <div class="details-row">
            <span class="details-label">Product Name:</span>
            <span class="details-value">${product.name}</span>
        </div>
        <div class="details-row">
            <span class="details-label">Category:</span>
            <span class="details-value">${product.category}</span>
        </div>
        <div class="details-row">
            <span class="details-label">Subcategory:</span>
            <span class="details-value">${product.subcategory}</span>
        </div>
        <div class="details-row">
            <span class="details-label">Brand:</span>
            <span class="details-value">${product.brand}</span>
        </div>
        <div class="details-row">
            <span class="details-label">Price:</span>
            <span class="details-value">₱${product.price}</span>
        </div>
    `;

  // Populate product images
  productImagesContent.innerHTML = product.images
    .map(
      (image) => `
        <div class="product-image">
            <img src="${image}" alt="Product Image">
        </div>
    `
    )
    .join("");

  // Populate description
  descriptionContent.innerHTML = `
        <p>${product.description}</p>
    `;

  // Populate stock details
  stockDetailsContent.innerHTML = `
        <table class="stock-table">
            <thead>
                <tr>
                    <th>Variation</th>
                    <th>Stock</th>
                    <th>SKU</th>
                </tr>
            </thead>
            <tbody>
                ${product.variations
                  .map(
                    (variation) => `
                    <tr>
                        <td>${variation.name}</td>
                        <td>${variation.stock}</td>
                        <td>${variation.sku}</td>
                    </tr>
                `
                  )
                  .join("")}
            </tbody>
        </table>
    `;

  // Show the modal
  productDetailsModal.style.display = "block";
}
