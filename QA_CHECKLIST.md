# Product Creation Flow - QA Checklist

## Pre-Testing Setup

- [ ] Run database migration: `python run_migration.py`
- [ ] Verify database tables exist: `product_variants`, `variant_sizes`, `product_descriptions`
- [ ] Ensure test seller account exists and is logged in
- [ ] Clear browser cache and localStorage

## Step 1: Basic Product Information

### Form Validation
- [ ] Product name is required (shows error if empty)
- [ ] Category is required (shows error if empty)
- [ ] Price accepts decimal values (e.g., 99.99)
- [ ] Discount percentage validates (0-100)
- [ ] Photo upload works for primary and secondary images

### Data Persistence
- [ ] Form data is saved when navigating to next step
- [ ] Images are properly uploaded and stored
- [ ] All form fields retain values when returning from later steps

## Step 2: Product Description

### Form Validation
- [ ] Description field accepts multi-line text
- [ ] Materials field accepts multi-line text
- [ ] Details & Fit field accepts multi-line text
- [ ] Certification checkboxes work correctly

### Data Persistence
- [ ] Description data is saved when navigating to next step
- [ ] Data persists when returning from Step 3

## Step 3: Stock Management

### Variant Creation
- [ ] "Add Variant" button creates new variant rows
- [ ] SKU field accepts alphanumeric input
- [ ] Color name and color picker sync bidirectionally
- [ ] Photo upload works for each variant
- [ ] "Select Sizes" modal opens and functions correctly

### Size Selection Modal
- [ ] Size groups display correctly (Clothing, Shoes, Rings, Misc)
- [ ] Clicking size boxes selects/deselects them
- [ ] Stock input appears when size is selected
- [ ] Custom size input allows adding custom sizes
- [ ] "Save" button applies selections and closes modal
- [ ] Size summary updates in the variant row

### Stock Calculations
- [ ] Row total stock updates when sizes are modified
- [ ] Overall total stock updates correctly
- [ ] Stock badges show correct colors (green/yellow/red)

### Form Submission
- [ ] "Save Product" button shows loading state
- [ ] Form submits via AJAX (no page reload)
- [ ] Success response navigates to preview page
- [ ] Error responses show appropriate messages

## Step 4: Preview Page

### Data Display
- [ ] Product name displays correctly
- [ ] Category and subcategory show properly
- [ ] Price displays with currency symbol
- [ ] Discount information shows if applicable
- [ ] Product images display correctly (clickable for full view)
- [ ] Description, materials, and details show formatted text
- [ ] Variants table shows all variants with correct data
- [ ] Size and stock information displays properly for each variant
- [ ] Color swatches show correct colors
- [ ] Stock badges use appropriate colors

### Navigation
- [ ] "Edit Product" button returns to stocks page
- [ ] "Publish Product" button shows loading state
- [ ] Successful publish redirects to Product Management
- [ ] Error messages display appropriately

## Step 5: Product Management

### Product List
- [ ] New product appears in the list
- [ ] Product shows as "Active" status (not draft)
- [ ] All product information displays correctly
- [ ] Images display properly in the list
- [ ] Stock levels show correctly

### Filtering
- [ ] "All" tab shows all products
- [ ] "Draft" tab shows only draft products
- [ ] "Active" tab shows only active products
- [ ] Counts in tabs are accurate

## Database Verification

### Product Record
- [ ] Product exists in `seller_product_management` table
- [ ] `is_draft` is FALSE after publishing
- [ ] `status` is 'active' after publishing
- [ ] All basic fields are populated correctly
- [ ] `variants` JSON contains correct structure

### Variant Structure
- [ ] Variants contain `sizeStocks` arrays
- [ ] Each size entry has `size` and `stock` properties
- [ ] Color information is preserved
- [ ] SKU information is preserved
- [ ] Photo URLs are valid

## Error Handling

### Validation Errors
- [ ] Missing required fields show clear error messages
- [ ] Invalid data types are rejected gracefully
- [ ] Network errors are handled appropriately
- [ ] Session timeout redirects to login

### Edge Cases
- [ ] Empty variants array is handled
- [ ] Zero stock quantities work correctly
- [ ] Very large stock numbers are accepted
- [ ] Special characters in product names work
- [ ] Long descriptions don't break layout

## Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (responsive design)

## Performance

- [ ] Page loads complete within 3 seconds
- [ ] Image uploads complete within 10 seconds
- [ ] Form submissions respond within 5 seconds
- [ ] No JavaScript errors in console
- [ ] No broken images or missing resources

## Sample Test Data

### Test Product 1: Simple Clothing Item
```json
{
  "productName": "Classic Cotton T-Shirt",
  "price": "29.99",
  "category": "clothing",
  "subcategory": "shirts",
  "description": "A comfortable, classic cotton t-shirt perfect for everyday wear.",
  "materials": "100% Cotton\nMachine wash cold\nTumble dry low",
  "variants": [
    {
      "sku": "CT-BLK-001",
      "color": "Black",
      "colorHex": "#000000",
      "sizeStocks": [
        {"size": "S", "stock": 10},
        {"size": "M", "stock": 15},
        {"size": "L", "stock": 8},
        {"size": "XL", "stock": 5}
      ]
    }
  ]
}
```

### Test Product 2: Multi-Variant Shoes
```json
{
  "productName": "Running Sneakers",
  "price": "89.99",
  "category": "shoes",
  "subcategory": "athletic",
  "description": "High-performance running sneakers with advanced cushioning.",
  "materials": "Synthetic mesh upper\nRubber sole\nWipe clean",
  "variants": [
    {
      "sku": "RS-BLK-001",
      "color": "Black",
      "colorHex": "#000000",
      "sizeStocks": [
        {"size": "US 8", "stock": 5},
        {"size": "US 9", "stock": 8},
        {"size": "US 10", "stock": 6}
      ]
    },
    {
      "sku": "RS-WHT-001", 
      "color": "White",
      "colorHex": "#FFFFFF",
      "sizeStocks": [
        {"size": "US 8", "stock": 3},
        {"size": "US 9", "stock": 7},
        {"size": "US 10", "stock": 4}
      ]
    }
  ]
}
```

## Acceptance Criteria Verification

- [ ] ✅ Save from add_product_stocks persists complete product record
- [ ] ✅ Product contains basic info, description, and variants with multiple sizes
- [ ] ✅ After save, UI navigates to Preview page
- [ ] ✅ Preview shows all fields exactly as stored in DB
- [ ] ✅ "Add Product" from Preview sets product as active
- [ ] ✅ User is redirected to Product Management after publishing
- [ ] ✅ API responses use clear JSON (no "validation passed" text)
- [ ] ✅ Database migration is reversible
- [ ] ✅ Changes are backwards-compatible with existing UI

## Sign-off

- [ ] Developer Testing Complete
- [ ] QA Testing Complete  
- [ ] Product Owner Approval
- [ ] Ready for Production Deployment

---

**Notes:**
- Test with both existing and new seller accounts
- Verify that existing products still work correctly
- Test the complete flow multiple times with different data
- Check browser developer console for any JavaScript errors
- Verify database queries are efficient (no N+1 problems)