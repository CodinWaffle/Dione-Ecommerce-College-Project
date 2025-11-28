// Quick test script to bypass validation and test product creation
// Paste this in browser console on the add_product_preview page

console.log("=== Quick Product Creation Test ===");

// Create minimal test data
const testPayload = {
  step1: {
    productName: "Test Product " + Date.now(),
    category: "Electronics",
    subcategory: "Phones",
    price: "199.99",
    discountType: "percentage",
    discountPercentage: "10",
    voucherType: "standard",
    primaryImage: "/static/image/banner.png",
    secondaryImage: "/static/image/banner.png"
  },
  step2: {
    description: "Test product description",
    materials: "Test materials",
    detailsFit: "Test fit details"
  },
  step3: {
    variants: [
      {
        sku: "TEST-001",
        color: "Red",
        colorHex: "#FF0000",
        size: "M",
        stock: 10,
        lowStock: 2
      }
    ],
    totalStock: 10
  }
};

console.log("Sending test payload:", testPayload);

// Send the request
fetch(window.location.pathname, {
  method: "POST",
  credentials: "same-origin",
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json, text/html",
  },
  body: JSON.stringify(testPayload),
})
.then(response => {
  console.log("Response status:", response.status);
  console.log("Response URL:", response.url);
  
  if (response.url && response.url.includes('/login')) {
    console.error("Authentication required - redirected to login");
    alert("You need to log in as a seller first!");
    return;
  }
  
  if (response.ok || response.status === 302) {
    console.log("✅ SUCCESS! Product creation worked!");
    alert("Success! Product was created. Redirecting to products page...");
    window.location.href = response.url || "/seller/products";
  } else {
    console.error("❌ Server error:", response.status);
    response.text().then(text => {
      console.error("Response text:", text);
      alert("Server error: " + response.status + "\nCheck console for details");
    });
  }
})
.catch(error => {
  console.error("❌ Network error:", error);
  alert("Network error: " + error.message);
});

console.log("Test request sent. Check network tab and console for results.");