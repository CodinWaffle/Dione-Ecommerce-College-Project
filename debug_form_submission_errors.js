// Debug script for form submission errors
// Paste this in browser console on the add_product_stocks page

console.log("=== Form Submission Debug Script ===");

// Check if there are any JavaScript errors
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    console.error('File:', e.filename);
    console.error('Line:', e.lineno);
});

// Override fetch to log all requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const [url, options] = args;
    
    console.log('🔍 FETCH REQUEST:', {
        url: url,
        method: options?.method || 'GET',
        headers: options?.headers || {},
        body: options?.body ? (typeof options.body === 'string' ? options.body.substring(0, 200) + '...' : '[FormData]') : null
    });
    
    return originalFetch.apply(this, args)
        .then(response => {
            console.log('📥 FETCH RESPONSE:', {
                url: url,
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries())
            });
            
            // Clone response to read it without consuming it
            const clonedResponse = response.clone();
            
            // Try to read response as text
            clonedResponse.text().then(text => {
                if (text.startsWith('<!DOCTYPE') || text.startsWith('<html')) {
                    console.warn('⚠️ RECEIVED HTML INSTEAD OF JSON:', text.substring(0, 200) + '...');
                } else {
                    console.log('📄 Response body:', text.substring(0, 200) + (text.length > 200 ? '...' : ''));
                }
            }).catch(e => {
                console.log('Could not read response body:', e);
            });
            
            return response;
        })
        .catch(error => {
            console.error('❌ FETCH ERROR:', {
                url: url,
                error: error.message
            });
            throw error;
        });
};

// Check form submission
const form = document.getElementById('productStocksForm');
if (form) {
    console.log('✅ Form found:', form);
    
    // Add form submit listener
    form.addEventListener('submit', function(e) {
        console.log('📝 FORM SUBMIT EVENT:', {
            action: form.action,
            method: form.method,
            elements: form.elements.length
        });
        
        // Log form data
        const formData = new FormData(form);
        console.log('📋 FORM DATA:');
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}: ${value}`);
        }
    });
} else {
    console.error('❌ Form not found!');
}

// Check for validation managers
if (window.ProductStockManager) {
    console.log('✅ ProductStockManager found');
} else {
    console.log('⚠️ ProductStockManager not found');
}

// Check for variant data
const variants = document.querySelectorAll('#variantTableBody tr');
console.log(`📊 Found ${variants.length} variant rows`);

variants.forEach((row, index) => {
    const sku = row.querySelector('input[name^="sku_"]')?.value;
    const color = row.querySelector('input[name^="color_"]')?.value;
    const sizeInputs = row.querySelectorAll('.size-stock-input');
    
    console.log(`Variant ${index + 1}:`, {
        sku: sku,
        color: color,
        sizes: sizeInputs.length
    });
});

console.log("=== Debug Script Ready ===");
console.log("Now try to submit the form and watch the console output.");