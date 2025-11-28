// Targeted fix for size validation tooltip issue
// This script only fixes the validation without interfering with form submission

document.addEventListener("DOMContentLoaded", function() {
    console.log("Size validation targeted fix loaded");
    
    // Only override the validation method, not the form submission
    if (window.ProductStockManager && window.ProductStockManager.prototype) {
        const originalCollectSizeStockData = window.ProductStockManager.prototype.collectSizeStockData;
        
        // Enhanced collectSizeStockData method
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
                        console.log(`Enhanced validation found ${sizes.length} sizes for variant ${variantNumber}`);
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
                        console.log(`Enhanced validation found ${sizes.length} sizes from checkboxes for variant ${variantNumber}`);
                        return sizes;
                    }
                }
            }
            
            // If our enhanced method didn't find anything, fall back to original method
            if (originalCollectSizeStockData) {
                const originalResult = originalCollectSizeStockData.call(this, variantNumber);
                if (originalResult && originalResult.length > 0) {
                    console.log(`Original method found ${originalResult.length} sizes for variant ${variantNumber}`);
                    return originalResult;
                }
            }
            
            console.log(`No sizes found for variant ${variantNumber}`);
            return sizes;
        };
        
        console.log("Enhanced size validation method applied");
    } else {
        console.log("ProductStockManager not found, validation fix not applied");
    }
    
    // Add a simple validation helper that doesn't interfere with form submission
    window.checkSizeSelection = function(variantNumber) {
        const variantRow = document.querySelector(
            `tr[data-variant="${variantNumber}"], #variantTableBody tr:nth-child(${variantNumber})`
        );
        
        if (!variantRow) return false;
        
        // Check multiple indicators of size selection
        const sizeStockInputs = variantRow.querySelectorAll('.size-stock-input');
        const checkedSizeBoxes = variantRow.querySelectorAll('.variant-size-checkbox:checked');
        const sizeSummary = variantRow.querySelector('.variant-size-summary');
        const hasSizeSummaryContent = sizeSummary && sizeSummary.textContent.trim() && 
                                    !sizeSummary.textContent.includes('No sizes selected');
        
        return sizeStockInputs.length > 0 || checkedSizeBoxes.length > 0 || hasSizeSummaryContent;
    };
    
    console.log("Size validation targeted fix applied successfully");
});