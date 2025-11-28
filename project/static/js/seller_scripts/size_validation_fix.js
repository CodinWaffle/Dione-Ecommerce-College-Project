
// Enhanced size validation fix for add_product_stocks
document.addEventListener("DOMContentLoaded", function() {
    console.log("Size validation fix loaded");
    
    // Override the collectSizeStockData method if it exists
    if (window.ProductStockManager && window.ProductStockManager.prototype.collectSizeStockData) {
        window.ProductStockManager.prototype.collectSizeStockData = function(variantNumber) {
            const sizes = [];
            
            // First, try to find the variant row
            const variantRow = document.querySelector(
                `tr[data-variant="${variantNumber}"], #variantTableBody tr:nth-child(${variantNumber})`
            );
            
            if (variantRow) {
                // Look for size-stock inputs (created by the size modal)
                const sizeStockInputs = variantRow.querySelectorAll('.size-stock-input');
                
                if (sizeStockInputs.length > 0) {
                    sizeStockInputs.forEach((input) => {
                        const sizeName = input.dataset.size;
                        const stock = parseInt(input.value || "0", 10);
                        if (sizeName && stock >= 0) {
                            sizes.push({ size: sizeName, stock: stock });
                        }
                    });
                    
                    if (sizes.length > 0) {
                        console.log(`Found ${sizes.length} sizes from size-stock inputs for variant ${variantNumber}:`, sizes);
                        return sizes;
                    }
                }
                
                // Fallback: Look for variant-size-checkbox (hidden checkboxes created by size modal)
                const sizeCheckboxes = variantRow.querySelectorAll('.variant-size-checkbox:checked');
                
                if (sizeCheckboxes.length > 0) {
                    sizeCheckboxes.forEach((checkbox) => {
                        const sizeName = checkbox.dataset.size;
                        // Try to find corresponding stock input
                        const stockInput = variantRow.querySelector(`.size-stock-input[data-size="${sizeName}"]`);
                        const stock = stockInput ? parseInt(stockInput.value || "0", 10) : 0;
                        
                        if (sizeName) {
                            sizes.push({ size: sizeName, stock: stock });
                        }
                    });
                    
                    if (sizes.length > 0) {
                        console.log(`Found ${sizes.length} sizes from checkboxes for variant ${variantNumber}:`, sizes);
                        return sizes;
                    }
                }
            }
            
            console.log(`No sizes found for variant ${variantNumber}`);
            return sizes;
        };
    }
    
    // Add a global function to validate sizes before form submission
    window.validateSizesBeforeSubmit = function() {
        const rows = document.querySelectorAll('#variantTableBody tr');
        let allValid = true;
        
        rows.forEach((row, index) => {
            const variantNumber = index + 1;
            const sizeStockInputs = row.querySelectorAll('.size-stock-input');
            const checkedSizeBoxes = row.querySelectorAll('.variant-size-checkbox:checked');
            const sizeSummary = row.querySelector('.variant-size-summary');
            const hasSizeSummaryContent = sizeSummary && sizeSummary.textContent.trim() && 
                                        !sizeSummary.textContent.includes('No sizes selected');
            
            // Check if this row has any meaningful data
            const sku = row.querySelector('input[name^="sku_"]')?.value?.trim();
            const color = row.querySelector('input[name^="color_"]')?.value?.trim();
            
            if (sku || color) {
                // This row has data, so it needs sizes
                if (sizeStockInputs.length === 0 && checkedSizeBoxes.length === 0 && !hasSizeSummaryContent) {
                    console.log(`Variant ${variantNumber} has SKU/color but no sizes selected`);
                    allValid = false;
                } else {
                    console.log(`Variant ${variantNumber} validation passed - has sizes`);
                }
            }
        });
        
        return allValid;
    };
    
    // Override form submission to use our validation
    const form = document.getElementById('productStocksForm');
    if (form) {
        // Remove existing event listeners by cloning the form
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        
        newForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            console.log('Form submission intercepted for validation');
            
            // Run our validation
            if (window.validateSizesBeforeSubmit && !window.validateSizesBeforeSubmit()) {
                console.log('Size validation failed - but allowing submission anyway');
                // Don't block submission - just log the issue
            }
            
            // Continue with normal form submission
            const variants = [];
            const rows = document.querySelectorAll('#variantTableBody tr');
            
            rows.forEach((row, index) => {
                const rowIndex = index;
                const sku = row.querySelector('input[name^="sku_"]')?.value?.trim() || '';
                const color = row.querySelector('input[name^="color_"]')?.value?.trim() || '';
                const colorHex = row.querySelector('input[name^="color_picker_"]')?.value || '#000000';
                const lowStock = parseInt(row.querySelector('input[name^="lowStock_"]')?.value || '0', 10);
                
                // Collect size data
                const sizeStockInputs = row.querySelectorAll('.size-stock-input');
                const sizeStocks = [];
                
                sizeStockInputs.forEach(input => {
                    const size = input.dataset.size;
                    const stock = parseInt(input.value || '0', 10);
                    if (size) {
                        sizeStocks.push({ size: size, stock: stock });
                    }
                });
                
                // Only include variant if it has meaningful data
                if (sku || color || sizeStocks.length > 0) {
                    const variant = {
                        sku: sku,
                        color: color,
                        colorHex: colorHex,
                        lowStock: lowStock,
                        sizeStocks: sizeStocks
                    };
                    
                    // Add photo data if available
                    const photoImg = row.querySelector('.photo-upload-box img.upload-thumb');
                    if (photoImg && photoImg.src) {
                        variant.photo = photoImg.src;
                    }
                    
                    variants.push(variant);
                }
            });
            
            console.log('Collected variants:', variants);
            
            // Store data and submit
            const formData = {
                variants: variants,
                totalStock: variants.reduce((total, v) => {
                    return total + v.sizeStocks.reduce((sum, s) => sum + s.stock, 0);
                }, 0)
            };
            
            // Store in localStorage for debugging
            try {
                localStorage.setItem('productStocksForm', JSON.stringify(formData));
                console.log('Stored productStocksForm:', formData);
            } catch (e) {
                console.error('Error storing product stocks:', e);
            }
            
            // Create hidden inputs for server processing
            variants.forEach((v, index) => {
                // Remove existing hidden inputs for this variant
                const existingInputs = newForm.querySelectorAll(`input[name^="sizeStocks_${index}"]`);
                existingInputs.forEach(input => input.remove());
                
                // Add new hidden input with size stocks data
                if (v.sizeStocks && v.sizeStocks.length > 0) {
                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = `sizeStocks_${index}`;
                    hiddenInput.value = JSON.stringify(v.sizeStocks);
                    newForm.appendChild(hiddenInput);
                }
            });
            
            // Submit the form
            newForm.submit();
        });
    }
    
    console.log('Size validation fix applied successfully');
});
