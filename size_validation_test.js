
// Test script for size validation
// Paste this in browser console on add_product_stocks page

console.log("=== Size Validation Test ===");

// Check if validation functions exist
console.log("validateSizesBeforeSubmit exists:", typeof window.validateSizesBeforeSubmit);

// Check current state
const rows = document.querySelectorAll('#variantTableBody tr');
console.log(`Found ${rows.length} variant rows`);

rows.forEach((row, index) => {
    const variantNumber = index + 1;
    const sizeStockInputs = row.querySelectorAll('.size-stock-input');
    const checkedSizeBoxes = row.querySelectorAll('.variant-size-checkbox:checked');
    const sizeSummary = row.querySelector('.variant-size-summary');
    const sku = row.querySelector('input[name^="sku_"]')?.value?.trim();
    const color = row.querySelector('input[name^="color_"]')?.value?.trim();
    
    console.log(`Variant ${variantNumber}:`);
    console.log(`  - SKU: "${sku}"`);
    console.log(`  - Color: "${color}"`);
    console.log(`  - Size stock inputs: ${sizeStockInputs.length}`);
    console.log(`  - Checked size boxes: ${checkedSizeBoxes.length}`);
    console.log(`  - Size summary: "${sizeSummary?.textContent?.trim()}"`);
    
    if (sizeStockInputs.length > 0) {
        console.log(`  - Sizes:`, Array.from(sizeStockInputs).map(input => ({
            size: input.dataset.size,
            stock: input.value
        })));
    }
});

// Test validation
if (window.validateSizesBeforeSubmit) {
    const isValid = window.validateSizesBeforeSubmit();
    console.log(`Validation result: ${isValid ? 'PASS' : 'FAIL'}`);
} else {
    console.log("Validation function not found");
}

console.log("=== Test Complete ===");
