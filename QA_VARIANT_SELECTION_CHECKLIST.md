# QA Checklist: Product Variant Selection & Stock Management

## Test Environment Setup

- [ ] Test database populated with products having multiple color variants
- [ ] Each color variant has multiple sizes with varying stock levels
- [ ] Include test cases with 0 stock, low stock (≤3), and normal stock levels
- [ ] Test both JSON variant structure (SellerProduct) and ProductVariant model
- [ ] Browser developer tools open for monitoring console logs and network requests

## Core Functionality Tests

### Color Selection

- [ ] **Initial State**: Verify sizes section shows "Select a color to view available sizes" placeholder
- [ ] **Color Selection**: Click each color option and verify:
  - [ ] Color becomes visually selected (active class applied)
  - [ ] Selected color name updates in UI
  - [ ] Color hex value is applied to CSS variables for theming
  - [ ] Previous color selection is cleared
  - [ ] Previous size selection is cleared when color changes

### Dynamic Size Loading

- [ ] **API Call Verification**:
  - [ ] Confirm GET request to `/api/products/{id}/colors/{color}/sizes`
  - [ ] Request includes proper URL encoding for color names with spaces/special chars
  - [ ] Response returns expected JSON structure with success, color, sizes, total_stock
- [ ] **Loading States**:
  - [ ] Loading spinner appears immediately when color is selected
  - [ ] "Loading available sizes..." message is shown
  - [ ] Loading state is accessible (aria-live announcements)
- [ ] **Size Rendering**:
  - [ ] Sizes are sorted logically (XS, S, M, L, XL, XXL, etc.)
  - [ ] Available sizes are clickable and properly styled
  - [ ] Out-of-stock sizes are disabled with visual indicators (✕ icon)
  - [ ] Low stock sizes show stock count ("3 left")
  - [ ] Each size has proper ARIA labels ("Size S, 15 available")

### Size Selection

- [ ] **Selection Behavior**:
  - [ ] Only one size can be selected at a time
  - [ ] Clicking disabled/out-of-stock sizes has no effect
  - [ ] Size selection triggers stock display update
  - [ ] Visual feedback (scaling, shadow) on selection
- [ ] **Stock Display**:
  - [ ] Stock indicator shows correct number for selected color+size
  - [ ] Stock display updates immediately upon size selection
  - [ ] Color coding: green (>3 stock), orange (1-3 stock), red (0 stock)

### Add to Cart Functionality

#### Validation Tests

- [ ] **Pre-Selection Validation**:
  - [ ] Clicking "Add to Cart" without color selection shows error
  - [ ] Clicking "Add to Cart" without size selection shows error
  - [ ] Error messages are clear and disappear after timeout
- [ ] **Stock Validation**:
  - [ ] Cannot add out-of-stock items (0 stock)
  - [ ] Cannot add quantity exceeding available stock
  - [ ] Server-side validation prevents race conditions
  - [ ] Error messages show available stock counts

#### Successful Add to Cart

- [ ] **API Request**:
  - [ ] POST to `/add-to-cart` with correct JSON payload
  - [ ] Includes product_id, color, size, quantity, color_hex, image_url
- [ ] **Response Handling**:
  - [ ] Success response updates cart count in UI
  - [ ] Remaining stock is updated in size button and stock display
  - [ ] Button shows success state briefly
- [ ] **Cart Session**:
  - [ ] Items stored in session with correct variant information
  - [ ] Duplicate items accumulate quantity correctly
  - [ ] Cart persists across page reloads

### Error Handling & Edge Cases

#### Network Issues

- [ ] **API Failure Simulation**:
  - [ ] Disconnect network and select colors
  - [ ] Verify fallback to cached/static data
  - [ ] Error message shown if no fallback available
  - [ ] Retry functionality works when network restored

#### Malformed Data

- [ ] **Invalid Product Data**:
  - [ ] Product with no variants shows appropriate message
  - [ ] Corrupted variant JSON doesn't break page
  - [ ] Missing color information handled gracefully
- [ ] **Edge Case Colors**:
  - [ ] Colors with special characters in names
  - [ ] Very long color names
  - [ ] Colors with no available sizes

#### Concurrency & Stock Updates

- [ ] **Race Condition Tests**:
  - [ ] Open product in multiple tabs
  - [ ] Add same variant to cart from multiple tabs simultaneously
  - [ ] Verify stock validation prevents overselling
  - [ ] Stock updates propagate correctly

## Accessibility Testing

### Screen Reader Support

- [ ] **Announcements**:
  - [ ] Color selection announced ("X sizes available for [color]")
  - [ ] Size availability changes announced
  - [ ] Loading states announced
  - [ ] Error states announced
- [ ] **Focus Management**:
  - [ ] Tab navigation works through colors and sizes
  - [ ] Focus indicators are visible
  - [ ] Focus trapped appropriately during loading

### ARIA Compliance

- [ ] **Labels and Descriptions**:
  - [ ] All buttons have descriptive aria-labels
  - [ ] Loading states use aria-live regions
  - [ ] Error messages associated with controls
  - [ ] Stock information accessible to screen readers
- [ ] **States**:
  - [ ] Disabled states properly marked with aria-disabled
  - [ ] Selected states indicated with aria-selected or aria-pressed
  - [ ] Loading states use appropriate ARIA attributes

## Performance Testing

### API Performance

- [ ] **Response Times**:
  - [ ] Size API responses under 200ms for typical products
  - [ ] No visible delay between color selection and size loading
  - [ ] Concurrent requests handled efficiently
- [ ] **Caching**:
  - [ ] Repeated color selections use cached data when appropriate
  - [ ] Browser cache headers set correctly for static resources

### Frontend Performance

- [ ] **DOM Updates**:
  - [ ] No visible layout shifts during size updates
  - [ ] Smooth animations and transitions
  - [ ] No memory leaks during repeated selections
- [ ] **Bundle Size**:
  - [ ] JavaScript bundle size impact minimal
  - [ ] CSS loading doesn't block functionality

## Browser Compatibility

### Desktop Browsers

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Mobile Browsers

- [ ] Mobile Chrome (Android)
- [ ] Safari (iOS)
- [ ] Samsung Internet

### Feature Support

- [ ] **JavaScript Features**:
  - [ ] Fetch API works or polyfill provided
  - [ ] Modern JavaScript features supported
  - [ ] CSS Grid/Flexbox layout works
- [ ] **Graceful Degradation**:
  - [ ] Basic functionality works without JavaScript
  - [ ] Progressive enhancement implemented

## Security Testing

### Input Validation

- [ ] **XSS Prevention**:
  - [ ] Color names properly escaped in HTML
  - [ ] User input sanitized before API calls
  - [ ] JSON responses properly parsed
- [ ] **CSRF Protection**:
  - [ ] Add to cart requests include CSRF tokens where required
  - [ ] API endpoints properly protected

### Data Handling

- [ ] **Session Security**:
  - [ ] Cart data encrypted in session
  - [ ] Sensitive information not exposed in client
  - [ ] Session timeout handled gracefully

## Integration Testing

### Database Operations

- [ ] **Variant Queries**:
  - [ ] Database queries efficient for large product catalogs
  - [ ] Proper indexes on variant lookup fields
  - [ ] Transaction handling for stock updates

### Third-party Integrations

- [ ] **Analytics**:
  - [ ] Color/size selection events tracked
  - [ ] Add-to-cart events properly logged
  - [ ] Error events captured for monitoring

## Regression Testing

### Existing Functionality

- [ ] **Product Display**:
  - [ ] Product images still display correctly
  - [ ] Product information unchanged
  - [ ] Other product page features unaffected
- [ ] **Navigation**:
  - [ ] Links and buttons still functional
  - [ ] Page routing unchanged
  - [ ] SEO meta tags preserved

## Deployment Checklist

### Production Readiness

- [ ] **Configuration**:
  - [ ] API endpoints configured for production
  - [ ] Error logging enabled
  - [ ] Performance monitoring active
- [ ] **Backup Plans**:
  - [ ] Rollback procedure documented
  - [ ] Feature flags implemented for gradual rollout
  - [ ] Monitoring alerts configured

### Post-Deployment Verification

- [ ] **Smoke Tests**:
  - [ ] Basic color/size selection works
  - [ ] Add to cart functionality works
  - [ ] No console errors on production
- [ ] **Monitoring**:
  - [ ] API response times within acceptable range
  - [ ] Error rates below threshold
  - [ ] User engagement metrics tracked

## Sample Test Data

### Test Product Setup

```json
{
  "product_id": 123,
  "name": "Test Product",
  "variants": [
    {
      "color": "Black",
      "colorHex": "#000000",
      "sizeStocks": [
        { "size": "XS", "stock": 0 }, // Out of stock
        { "size": "S", "stock": 2 }, // Low stock
        { "size": "M", "stock": 15 }, // Normal stock
        { "size": "L", "stock": 8 }, // Normal stock
        { "size": "XL", "stock": 1 } // Low stock
      ]
    },
    {
      "color": "Red",
      "colorHex": "#ff0000",
      "sizeStocks": [
        { "size": "S", "stock": 5 },
        { "size": "M", "stock": 12 },
        { "size": "L", "stock": 0 } // Out of stock
      ]
    }
  ]
}
```

## Test Execution Notes

### Testing Order

1. Run unit tests first to verify API functionality
2. Perform manual UI tests for core functionality
3. Execute accessibility tests
4. Run performance benchmarks
5. Complete browser compatibility testing
6. Perform security validation
7. Execute integration tests
8. Final regression testing

### Bug Reporting Template

```
Title: [Component] - [Brief Description]
Severity: Critical/High/Medium/Low
Steps to Reproduce:
1.
2.
3.

Expected Result:
Actual Result:
Browser/Version:
Test Data Used:
Screenshots/Videos:
Console Errors:
```
