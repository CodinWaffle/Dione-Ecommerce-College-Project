# Product Variant API Documentation

## Overview

This document describes the API endpoints for product variant selection and stock management in the e-commerce product detail system.

## Base URL

```
Production: https://your-domain.com/api
Development: http://localhost:5000/api
```

## Authentication

Most endpoints are public. Cart operations may require session authentication.

## Endpoints

### Get Sizes for Product Color

Retrieves available sizes and stock information for a specific product color variant.

**Endpoint**: `GET /api/products/{product_id}/colors/{color}/sizes`

**Parameters**:

- `product_id` (integer, required) - The unique identifier of the product
- `color` (string, required) - The color variant name (URL encoded if contains spaces/special chars)

**Example Request**:

```bash
curl -X GET "https://your-domain.com/api/products/123/colors/Black/sizes" \
  -H "Accept: application/json"
```

**Example Request with URL Encoding**:

```bash
curl -X GET "https://your-domain.com/api/products/123/colors/Navy%20Blue/sizes" \
  -H "Accept: application/json"
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "color": "Black",
  "sizes": [
    {
      "size": "XS",
      "stock": 10,
      "available": true,
      "low_stock": false,
      "sku": "PROD-123-BLACK-XS"
    },
    {
      "size": "S",
      "stock": 3,
      "available": true,
      "low_stock": true,
      "sku": "PROD-123-BLACK-S"
    },
    {
      "size": "M",
      "stock": 15,
      "available": true,
      "low_stock": false,
      "sku": "PROD-123-BLACK-M"
    },
    {
      "size": "L",
      "stock": 0,
      "available": false,
      "low_stock": false,
      "sku": "PROD-123-BLACK-L"
    }
  ],
  "total_stock": 28,
  "variant_id": 456
}
```

**Error Response - Color Not Found** (404 Not Found):

```json
{
  "success": false,
  "error": "Color variant not found",
  "color": "Purple"
}
```

**Error Response - Product Not Found** (404 Not Found):

```json
{
  "success": false,
  "error": "Product not found"
}
```

**Error Response - Server Error** (500 Internal Server Error):

```json
{
  "success": false,
  "error": "Server error",
  "detail": "Database connection failed"
}
```

**Response Fields**:

- `success` (boolean) - Indicates if request was successful
- `color` (string) - The requested color name
- `sizes` (array) - List of available sizes
  - `size` (string) - Size label (e.g., "XS", "S", "M", "L", "XL")
  - `stock` (integer) - Available stock count
  - `available` (boolean) - Whether size is in stock (stock > 0)
  - `low_stock` (boolean) - Whether stock is low (stock <= 3 and stock > 0)
  - `sku` (string, optional) - Stock keeping unit identifier
- `total_stock` (integer) - Total stock across all sizes for this color
- `variant_id` (integer, optional) - Database variant ID (for ProductVariant model)

### Add Item to Cart

Adds a product variant to the shopping cart with stock validation.

**Endpoint**: `POST /api/add-to-cart`

**Content-Type**: `application/json`

**Request Body**:

```json
{
  "product_id": 123,
  "color": "Black",
  "size": "M",
  "quantity": 2,
  "color_hex": "#000000",
  "image_url": "/static/uploads/product-123-main.jpg"
}
```

**Request Fields**:

- `product_id` (integer, required) - Product identifier
- `color` (string, required) - Selected color variant
- `size` (string, required) - Selected size
- `quantity` (integer, required) - Quantity to add (must be > 0)
- `color_hex` (string, optional) - Hex color code for UI styling
- `image_url` (string, optional) - Product image URL for cart display

**Example Request**:

```bash
curl -X POST "https://your-domain.com/api/add-to-cart" \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{
    "product_id": 123,
    "color": "Black",
    "size": "M",
    "quantity": 1,
    "color_hex": "#000000",
    "image_url": "/static/uploads/black-shirt.jpg"
  }'
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "message": "Added 1 item(s) to cart",
  "cart_count": 3,
  "remaining_stock": 14
}
```

**Error Response - Missing Fields** (400 Bad Request):

```json
{
  "error": "Missing required fields: product_id, color, size required"
}
```

**Error Response - Out of Stock** (409 Conflict):

```json
{
  "error": "Out of stock",
  "message": "Sorry, Black in size M is currently out of stock."
}
```

**Error Response - Insufficient Stock** (409 Conflict):

```json
{
  "error": "Insufficient stock",
  "message": "Only 5 items available for Black in size M.",
  "available_stock": 5
}
```

**Error Response - Exceeds Cart Limit** (409 Conflict):

```json
{
  "error": "Exceeds available stock",
  "message": "You have 2 of this item in cart. Only 3 more can be added.",
  "available_to_add": 3
}
```

**Success Response Fields**:

- `success` (boolean) - Operation success indicator
- `message` (string) - Human-readable success message
- `cart_count` (integer) - Total items in cart after addition
- `remaining_stock` (integer) - Stock remaining after this addition

## Data Models

### Variant Structure (JSON Format)

```json
{
  "color": "Black",
  "colorHex": "#000000",
  "sizeStocks": [
    {
      "size": "XS",
      "stock": 10
    },
    {
      "size": "S",
      "stock": 15
    }
  ]
}
```

### Legacy Variant Structure

```json
{
  "color": "Black",
  "colorHex": "#000000",
  "size": "M",
  "stock": 20
}
```

### Database Models

**SellerProduct** (Primary product table):

- Uses JSON `variants` field for flexible variant storage
- Supports both new and legacy variant structures

**ProductVariant** (Normalized variant table):

- `id` - Primary key
- `product_id` - Foreign key to SellerProduct
- `variant_name` - Color name
- `variant_sku` - Variant-level SKU
- `images_json` - Variant-specific images

**VariantSize** (Individual size records):

- `id` - Primary key
- `variant_id` - Foreign key to ProductVariant
- `size_label` - Size name (XS, S, M, etc.)
- `stock_quantity` - Available stock
- `sku` - Size-specific SKU

## Frontend Integration

### JavaScript Usage Example

```javascript
// Fetch sizes when color is selected
async function fetchAvailableSizes(color, productId) {
  try {
    const response = await fetch(
      `/api/products/${productId}/colors/${encodeURIComponent(color)}/sizes`
    );
    const data = await response.json();

    if (data.success) {
      renderSizeOptions(data.sizes);
      updateStockData(color, data.sizes);
    } else {
      showError(data.error);
    }
  } catch (error) {
    console.error("Failed to fetch sizes:", error);
    showFallbackSizes(color);
  }
}

// Add to cart with validation
async function addToCart(itemData) {
  try {
    const response = await fetch("/api/add-to-cart", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(itemData),
    });

    const result = await response.json();

    if (response.ok && result.success) {
      updateCartCount(result.cart_count);
      updateStockDisplay(result.remaining_stock);
      showSuccessMessage(result.message);
    } else {
      showErrorMessage(result.message || result.error);
    }
  } catch (error) {
    console.error("Add to cart failed:", error);
    showErrorMessage("Network error. Please try again.");
  }
}
```

### Size Rendering Example

```javascript
function renderSizeOptions(sizes) {
  const container = document.getElementById("sizeOptions");

  const html = sizes
    .map((sizeInfo) => {
      const { size, stock, available, low_stock } = sizeInfo;
      const cssClasses = [
        "size-option",
        !available && "disabled out-of-stock",
        low_stock && "low-stock",
      ]
        .filter(Boolean)
        .join(" ");

      return `
      <button 
        class="${cssClasses}"
        data-size="${size}"
        data-stock="${stock}"
        ${!available ? "disabled" : ""}
        aria-label="Size ${size}, ${stock} available"
      >
        <span class="size-label">${size}</span>
        ${low_stock ? `<span class="stock-info">${stock} left</span>` : ""}
        ${!available ? '<span class="oos-indicator">✕</span>' : ""}
      </button>
    `;
    })
    .join("");

  container.innerHTML = html;
}
```

## Rate Limits

- **Size API**: 60 requests per minute per IP
- **Add to Cart**: 30 requests per minute per session

## Caching

### Client-Side Caching

- Size data cached for 5 minutes per color/product combination
- Cache invalidated on stock updates

### Server-Side Caching

- Database queries cached for 30 seconds
- Cache invalidated on inventory updates

## Error Handling Best Practices

### Frontend Error Handling

1. **Network Errors**: Show user-friendly message and retry option
2. **Validation Errors**: Display specific field validation messages
3. **Stock Errors**: Update UI to reflect current stock levels
4. **Loading States**: Show appropriate loading indicators

### Backend Error Responses

1. **Consistent Format**: All errors return JSON with error field
2. **Meaningful Messages**: User-facing error messages
3. **Proper HTTP Status**: Use appropriate status codes
4. **Logging**: Log errors for monitoring and debugging

## Security Considerations

### Input Validation

- Sanitize all input parameters
- Validate product IDs exist and are accessible
- Check quantity limits and data types

### Rate Limiting

- Implement rate limiting on API endpoints
- Prevent abuse of cart operations

### Session Security

- Validate session tokens for cart operations
- Implement CSRF protection where needed

## Monitoring & Analytics

### Key Metrics

- API response times for size fetching
- Add to cart success/failure rates
- Stock-out frequency by product/variant
- User interaction patterns with variants

### Error Monitoring

- Track API error rates and types
- Monitor JavaScript errors in size selection
- Alert on high failure rates

## Testing

### API Testing

```bash
# Test size endpoint
curl -X GET "http://localhost:5000/api/products/1/colors/Black/sizes"

# Test add to cart
curl -X POST "http://localhost:5000/api/add-to-cart" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"color":"Black","size":"M","quantity":1}'
```

### Load Testing

- Test size API with concurrent requests
- Verify cart operations under load
- Check database performance with large product catalogs
