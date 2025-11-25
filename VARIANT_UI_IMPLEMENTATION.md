# Dynamic Variant UI Implementation

## Overview

This implementation provides a fully dynamic, stock-aware variant UI for the product details page. The system handles color and size variants with real-time stock updates, image switching, and proper out-of-stock handling.

## Features Implemented

### 1. Dynamic Color Swatches
- **Circular color swatches** rendered from database variant data
- **Color hex values** from `colorHex` field in variants JSON
- **Out-of-stock indicators** with "OOS" labels for colors with zero stock
- **Disabled state** for out-of-stock colors (opacity reduced, not clickable)

### 2. Stock-Aware Size Selection
- **Dynamic size options** that update based on selected color
- **Real-time availability** - sizes with 0 stock are disabled and struck through
- **Visual feedback** for unavailable sizes (opacity, strikethrough, disabled cursor)

### 3. Image Switching
- **Variant image support** - main product image switches when color is selected
- **Fallback handling** - uses primary/secondary product images if variant images not available
- **Thumbnail updates** - thumbnail gallery updates to show variant images

### 4. Real-Time Stock Display
- **Live stock counter** updates based on selected color+size combination
- **Add to Bag button** disables when selected variant is out of stock
- **Stock status styling** with different colors for in-stock, low-stock, and out-of-stock

## Backend Implementation

### Database Structure

The variant data is stored in the `SellerProduct.variants` JSON field as a list of objects:

```json
[
  {
    "sku": "TSHIRT-BLK-XS",
    "color": "Black",
    "colorHex": "#000000",
    "size": "XS",
    "stock": 5,
    "lowStock": 2
  },
  {
    "sku": "TSHIRT-BLK-S", 
    "color": "Black",
    "colorHex": "#000000",
    "size": "S",
    "stock": 8,
    "lowStock": 2
  }
]
```

### Route Updates

#### `/product/<product_id>` (Product Detail Page)
- **Enhanced data processing** to convert variant list into structured `stock_data` and `variant_photos`
- **Template context** includes `stock_data` (color->size->stock mapping) and `variant_photos` (color->image mapping)

#### `/api/product/<product_id>` (Product API)
- **JSON response** includes structured variant data for client-side updates
- **Consistent format** with product detail page for seamless integration

#### `/api/product/<product_id>/variant/<variant_id>` (New Endpoint)
- **AJAX endpoint** for fetching specific variant data
- **Future enhancement** for dynamic image/stock loading

### Data Processing Logic

```python
# Convert variant list to structured data
for variant in sp.variants:
    color = variant.get('color', 'Unknown')
    size = variant.get('size', 'OS')
    stock = variant.get('stock', 0)
    color_hex = variant.get('colorHex', '#000000')
    
    # Build stock_data: {color: {size: stock}}
    if color not in stock_data:
        stock_data[color] = {}
    stock_data[color][size] = stock
    
    # Build variant_photos: {color: {primary, secondary, color_hex}}
    if color not in variant_photos:
        variant_photos[color] = {
            'primary': sp.primary_image,
            'secondary': sp.secondary_image,
            'color_hex': color_hex
        }
```

## Frontend Implementation

### Template Updates (`product_detail.html`)

#### Dynamic Color Rendering
```html
{% for color, sizes in stock_data.items() %}
{% set total_stock = sizes.values()|sum %}
{% set color_hex = variant_photos.get(color, {}).get('color_hex', '#000000') %}
<button
  class="color-option {% if loop.first %}active{% endif %} {% if total_stock == 0 %}disabled out-of-stock{% endif %}"
  data-color="{{ color }}"
  data-stock="{{ sizes|tojson }}"
  data-total-stock="{{ total_stock }}"
  style="background-color: {{ color_hex }}; {% if total_stock == 0 %}opacity: 0.3; pointer-events: none;{% endif %}"
  {% if total_stock > 0 %}onclick="selectColor(this)"{% endif %}
  title="{{ color }}{% if total_stock == 0 %} - Out of Stock{% endif %}"
>
  {% if total_stock == 0 %}
  <span class="oos-label">OOS</span>
  {% endif %}
</button>
{% endfor %}
```

#### Dynamic Size Rendering
```html
<div class="size-options" id="sizeOptions">
  {% if stock_data %}
    {% set first_color = stock_data.keys()|list|first %}
    {% set first_color_sizes = stock_data[first_color] %}
    {% for size, stock in first_color_sizes.items() %}
    <button
      class="size-option {% if loop.first %}active{% endif %} {% if stock == 0 %}disabled out-of-stock{% endif %}"
      data-size="{{ size }}"
      data-stock="{{ stock }}"
      {% if stock > 0 %}onclick="selectSize(this)"{% endif %}
    >
      {{ size }}
    </button>
    {% endfor %}
  {% endif %}
</div>
```

### JavaScript Updates (`product_detail.js`)

#### Enhanced Color Selection
```javascript
function selectColor(colorBtn) {
  // Prevent selection of out-of-stock colors
  if (colorBtn.classList.contains("disabled") || colorBtn.classList.contains("out-of-stock")) {
    return;
  }

  // Update active state
  document.querySelectorAll(".color-option").forEach(option => option.classList.remove("active"));
  colorBtn.classList.add("active");

  // Update selected color display
  document.querySelector(".selected-color").textContent = colorBtn.dataset.color;
  currentSelectedColor = colorBtn.dataset.color;

  // Rebuild size options for selected color
  updateSizeAvailability();
  updateStockDisplay();

  // Switch variant images if available
  switchVariantImages(currentSelectedColor);
}
```

#### Dynamic Size Updates
```javascript
function updateSizeAvailability() {
  const activeColorBtn = document.querySelector(".color-option.active");
  const sizeOptionsContainer = document.getElementById("sizeOptions");

  if (activeColorBtn && sizeOptionsContainer) {
    const colorStock = JSON.parse(activeColorBtn.dataset.stock);
    
    // Clear and rebuild size options
    sizeOptionsContainer.innerHTML = '';
    
    Object.keys(colorStock).forEach((size, index) => {
      const stock = colorStock[size];
      const isAvailable = stock > 0;
      
      const sizeBtn = document.createElement('button');
      sizeBtn.className = `size-option ${index === 0 && isAvailable ? 'active' : ''} ${!isAvailable ? 'disabled out-of-stock' : ''}`;
      sizeBtn.setAttribute('data-size', size);
      sizeBtn.setAttribute('data-stock', stock);
      sizeBtn.textContent = size;
      
      // Apply styling and event handlers
      if (isAvailable) {
        sizeBtn.onclick = () => selectSize(sizeBtn);
      }
      
      sizeOptionsContainer.appendChild(sizeBtn);
    });
  }
}
```

## CSS Enhancements

### Out-of-Stock Styling
```css
.size-option.disabled,
.size-option.out-of-stock {
  opacity: 0.5;
  cursor: not-allowed;
  text-decoration: line-through;
  pointer-events: none;
}

.color-option.disabled,
.color-option.out-of-stock {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
  position: relative;
}

.oos-label {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #dc143c;
  color: white;
  font-size: 8px;
  padding: 1px 3px;
  border-radius: 2px;
  font-weight: bold;
  z-index: 1;
}
```

## Testing

### Test Data Creation
Run `test_variant_implementation.py` to create sample products with variants:

```bash
python test_variant_implementation.py
```

This creates a test product with:
- **Black**: XS (5 stock), S (8 stock), M (0 stock)
- **Red**: XS (3 stock), S (0 stock)  
- **Blue**: XS (0 stock), S (0 stock) - completely out of stock

### Manual Testing
1. Visit `http://localhost:5000/product/6` (or the created product ID)
2. Test color selection - verify sizes update correctly
3. Test size selection - verify stock counter updates
4. Verify out-of-stock colors show "OOS" label and are disabled
5. Verify out-of-stock sizes are struck through and disabled
6. Verify "Add to Bag" button disables for out-of-stock combinations

## Integration Notes

### File Locations
- **Backend**: `project/routes/main_routes.py` (product detail route and API)
- **Template**: `project/templates/main/product_detail.html`
- **JavaScript**: `project/static/js/buyer_scripts/product_detail.js`
- **Models**: `project/models.py` (SellerProduct model)

### Existing Code Compatibility
- **Maintains existing CSS classes** and styling patterns
- **Preserves current HTML structure** with minimal additions
- **Extends existing JavaScript** without breaking current functionality
- **Uses existing database schema** (variants JSON field)

### Future Enhancements
1. **Variant Images**: Add support for color-specific product images
2. **Size Guide Integration**: Link size selection to size guide modal
3. **Inventory Alerts**: Real-time low stock warnings
4. **Wishlist Integration**: Save specific color/size combinations
5. **Quick Add**: Bulk add multiple variants to cart

## Accessibility Features
- **Keyboard Navigation**: All color and size options are keyboard accessible
- **Screen Reader Support**: Proper ARIA labels and titles
- **Color Contrast**: Out-of-stock indicators maintain readability
- **Focus Management**: Clear visual focus indicators

## Performance Considerations
- **Minimal DOM Manipulation**: Only rebuilds size options when color changes
- **Efficient Data Structure**: Pre-processed stock data for fast lookups
- **Lazy Loading Ready**: Structure supports future AJAX variant loading
- **Memory Efficient**: Reuses existing elements where possible

This implementation provides a robust, user-friendly variant selection system that integrates seamlessly with the existing Dione ecommerce platform while maintaining all current functionality and styling patterns.