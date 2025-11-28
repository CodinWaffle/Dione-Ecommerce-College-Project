// Temporary fix to bypass validation and debug the actual issue
// Paste this in browser console on the add_product_preview page

console.log("=== Applying Temporary Validation Bypass ===");

// Find the submit button
const submitBtn = document.getElementById("submitBtn");
if (!submitBtn) {
    console.error("Submit button not found!");
} else {
    console.log("Submit button found, removing existing listeners...");
    
    // Clone the button to remove all event listeners
    const newSubmitBtn = submitBtn.cloneNode(true);
    submitBtn.parentNode.replaceChild(newSubmitBtn, submitBtn);
    
    // Add new event listener without validation
    newSubmitBtn.addEventListener("click", function () {
        console.log("=== Bypass Submit Clicked ===");
        
        // Show loading state
        const originalText = newSubmitBtn.innerHTML;
        newSubmitBtn.disabled = true;
        newSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        
        // Get data without validation
        function safeParse(key) {
            try {
                let raw = localStorage.getItem(key) || sessionStorage.getItem(key);
                return raw ? JSON.parse(raw) : {};
            } catch (e) {
                console.warn("Failed to parse", key, e);
                return {};
            }
        }
        
        const basicInfo = safeParse("productForm");
        const description = safeParse("productDescriptionForm");
        const stock = safeParse("productStocksForm");
        
        console.log("Data being sent:", { basicInfo, description, stock });
        
        // Create minimal valid payload
        const payload = {
            step1: {
                productName: basicInfo.productName || basicInfo.product_name || basicInfo.name || "Test Product",
                category: basicInfo.category || basicInfo.productCategory || "Test Category",
                price: basicInfo.price || "100",
                ...basicInfo
            },
            step2: {
                description: description.description || "Test description",
                ...description
            },
            step3: {
                variants: stock.variants || [],
                totalStock: stock.totalStock || 0,
                ...stock
            }
        };
        
        console.log("Final payload:", payload);
        
        // Send request
        fetch(window.location.pathname, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json, text/html",
            },
            body: JSON.stringify(payload),
        })
        .then(response => {
            console.log("Response status:", response.status);
            console.log("Response URL:", response.url);
            
            if (response.url && response.url.includes('/login')) {
                alert("Session expired - redirecting to login");
                window.location.href = '/login';
                return;
            }
            
            if (response.ok || response.status === 302) {
                console.log("Success! Redirecting...");
                window.location.href = response.url || "/seller/products";
            } else {
                console.error("Server error:", response.status);
                response.text().then(text => {
                    console.error("Response text:", text);
                    alert("Server error: " + response.status);
                    newSubmitBtn.disabled = false;
                    newSubmitBtn.innerHTML = originalText;
                });
            }
        })
        .catch(error => {
            console.error("Network error:", error);
            alert("Network error: " + error.message);
            newSubmitBtn.disabled = false;
            newSubmitBtn.innerHTML = originalText;
        });
    });
    
    console.log("✓ Validation bypass applied. Try clicking 'Add Product' now.");
    console.log("This will attempt to submit with minimal validation.");
}