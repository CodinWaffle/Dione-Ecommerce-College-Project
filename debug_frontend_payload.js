// Real-time frontend debugging script
// Paste this in browser console on the add_product_preview page

console.log("=== Frontend Payload Debug ===");

// Override the fetch function to intercept the request
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const [url, options] = args;
    
    if (url.includes('add_product_preview') && options && options.method === 'POST') {
        console.log("🔍 INTERCEPTED ADD_PRODUCT_PREVIEW REQUEST");
        console.log("URL:", url);
        console.log("Options:", options);
        
        if (options.body) {
            try {
                const payload = JSON.parse(options.body);
                console.log("📦 PAYLOAD BEING SENT:");
                console.log(JSON.stringify(payload, null, 2));
                
                // Check specific fields
                console.log("🔍 FIELD ANALYSIS:");
                console.log("step1.productName:", payload.step1?.productName);
                console.log("step1.category:", payload.step1?.category);
                console.log("step1.subcategory:", payload.step1?.subcategory);
                console.log("step1.price:", payload.step1?.price);
                
                // Check if fields are empty
                const issues = [];
                if (!payload.step1?.productName || payload.step1.productName.trim() === '') {
                    issues.push("productName is empty");
                }
                if (!payload.step1?.category || payload.step1.category.trim() === '') {
                    issues.push("category is empty");
                }
                if (!payload.step1?.price || payload.step1.price.trim() === '') {
                    issues.push("price is empty");
                }
                
                if (issues.length > 0) {
                    console.error("❌ ISSUES FOUND IN PAYLOAD:");
                    issues.forEach(issue => console.error("  -", issue));
                } else {
                    console.log("✅ All required fields present in payload");
                }
                
            } catch (e) {
                console.error("Failed to parse request body:", e);
            }
        }
    }
    
    return originalFetch.apply(this, args);
};

console.log("✅ Fetch interceptor installed. Now click 'Add Product' to see the actual payload being sent.");

// Also check current storage state
console.log("\n=== CURRENT STORAGE STATE ===");

const storageKeys = ['productForm', 'productDescriptionForm', 'productStocksForm', 'product_form_data'];
storageKeys.forEach(key => {
    const localData = localStorage.getItem(key);
    const sessionData = sessionStorage.getItem(key);
    
    console.log(`\n--- ${key} ---`);
    if (localData) {
        console.log("localStorage:", localData);
        try {
            const parsed = JSON.parse(localData);
            if (key === 'productForm' || key === 'product_form_data') {
                console.log("  productName:", parsed.productName);
                console.log("  category:", parsed.category);
                console.log("  price:", parsed.price);
            }
        } catch (e) {
            console.error("  Failed to parse localStorage data");
        }
    }
    
    if (sessionData) {
        console.log("sessionStorage:", sessionData);
        try {
            const parsed = JSON.parse(sessionData);
            if (key === 'productForm' || key === 'product_form_data') {
                console.log("  productName:", parsed.productName);
                console.log("  category:", parsed.category);
                console.log("  price:", parsed.price);
            }
        } catch (e) {
            console.error("  Failed to parse sessionStorage data");
        }
    }
    
    if (!localData && !sessionData) {
        console.log("No data found");
    }
});

console.log("\n=== READY FOR TESTING ===");
console.log("1. Check the storage state above");
console.log("2. Click 'Add Product' button");
console.log("3. Check the intercepted payload");
console.log("4. Compare with what you see in the database");