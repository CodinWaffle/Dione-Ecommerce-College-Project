#!/usr/bin/env python3
"""
Fix for product creation authentication and error handling
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def fix_authentication_issues():
    """Apply fixes for authentication and error handling"""
    
    print("=== Applying Product Creation Fixes ===")
    
    # Fix 1: Update the JavaScript to handle authentication errors
    js_fix = '''
// Enhanced error handling for authentication and server issues
(function () {
  function safeParse(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || "null");
    } catch (e) {
      return null;
    }
  }

  const submitBtn = document.getElementById("submitBtn");
  if (!submitBtn) return;
  
  submitBtn.addEventListener("click", function () {
    // Show loading state
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    
    // Attempt server-side save first (send JSON); if it fails, fall back to client-local flow
    (async function tryServerSave() {
      try {
        const basicInfo = safeParse("productForm") || {};
        const description = safeParse("productDescriptionForm") || {};
        const stock = safeParse("productStocksForm") || {};

        // Validate required fields before sending
        if (!basicInfo.productName || !basicInfo.category) {
          alert("Please fill in all required fields (Product Name and Category)");
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          return;
        }

        const payload = {
          step1: basicInfo,
          step2: description,
          step3: stock,
        };

        const res = await fetch(window.location.pathname, {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json, text/html",
          },
          body: JSON.stringify(payload),
        });

        // Check for authentication redirect
        if (res.url && res.url.includes('/login')) {
          alert("Your session has expired. Please log in again.");
          window.location.href = '/login';
          return;
        }

        if (res.ok) {
          // Success - redirect to products page
          const loc = res.url || "/seller/products";
          window.location.href = loc;
          return;
        } else {
          // Server error - show error message
          const errorText = await res.text();
          console.error("Server error:", res.status, errorText);
          alert("Error saving product. Please try again or contact support.");
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          return;
        }
      } catch (err) {
        console.warn("Server save failed, falling back to client-only save", err);
        
        // Check if it's a network error
        if (err.name === 'TypeError' && err.message.includes('fetch')) {
          alert("Network error. Please check your connection and try again.");
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          return;
        }
      }

      // Client-only localStorage flow (fallback)
      try {
        const basicInfo = safeParse("productForm") || {};
        const description = safeParse("productDescriptionForm") || {};
        const stock = safeParse("productStocksForm") || {};

        // Validate required fields
        if (!basicInfo.productName || !basicInfo.category) {
          alert("Please fill in all required fields (Product Name and Category)");
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          return;
        }

        // Build product object for the management list (keep full details inside object)
        const products = JSON.parse(localStorage.getItem("products") || "[]");
        const nextId =
          (products.reduce((m, p) => Math.max(m, Number(p.id || 0)), 0) || 0) + 1;

        const product = {
          id: nextId,
          name: basicInfo.productName || "Untitled Product",
          image: basicInfo.primaryImage || basicInfo.secondaryImage || "/static/image/banner.png",
          images: collectPreviewImages(basicInfo),
          price: Number(basicInfo.price) || 0,
          stock: Number(stock.totalStock) || (stock.variants ? stock.variants.reduce((s, v) => s + (Number(v.stock) || 0), 0) : 0),
          status: "active",
          category: basicInfo.category || "Uncategorized",
          // store full payload for preview/details modal
          _full: {
            basicInfo: basicInfo,
            description: description,
            stock: stock,
          },
          variants: stock.variants || [],
        };

        products.push(product);
        localStorage.setItem("products", JSON.stringify(products));

        // Clear draft forms
        try {
          localStorage.removeItem("productForm");
          localStorage.removeItem("productDescriptionForm");
          localStorage.removeItem("productStocksForm");
        } catch (e) {
          console.warn("Failed to clear draft after add", e);
        }

        // Show success message
        alert("Product saved locally. Note: This will only be visible in this browser.");
        
        // Redirect to product management page
        window.location.href = "/seller/products";
        
      } catch (localErr) {
        console.error("Local save also failed:", localErr);
        alert("Failed to save product. Please try again or contact support.");
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    })();
  });
})();
'''
    
    # Write the enhanced JavaScript
    with open('project/static/js/seller_scripts/add_product_preview_enhanced.js', 'w') as f:
        # Read the original file first
        try:
            with open('project/static/js/seller_scripts/add_product_preview.js', 'r') as orig:
                original_content = orig.read()
            
            # Replace the submit button handler
            start_marker = "// When Add Product is clicked:"
            end_marker = "})();"
            
            start_idx = original_content.find(start_marker)
            if start_idx != -1:
                end_idx = original_content.rfind(end_marker) + len(end_marker)
                if end_idx > start_idx:
                    # Replace the handler
                    new_content = (
                        original_content[:start_idx] + 
                        "// Enhanced Add Product handler with authentication and error handling\n" +
                        js_fix
                    )
                    f.write(new_content)
                    print("✓ Enhanced JavaScript created")
                else:
                    f.write(original_content + "\n\n" + js_fix)
                    print("✓ Enhanced JavaScript appended")
            else:
                f.write(original_content + "\n\n" + js_fix)
                print("✓ Enhanced JavaScript appended")
                
        except FileNotFoundError:
            f.write(js_fix)
            print("✓ New enhanced JavaScript created")
    
    # Fix 2: Add better error handling to the Flask route
    route_fix = '''
# Enhanced error handling for add_product_preview route
@seller_bp.route('/add_product_preview', methods=['GET', 'POST'])
def add_product_preview():
    """Add new product - Step 4: Preview
    
    Displays all collected data for review.
    On POST: Inserts product into database and clears session.
    """
    if request.method == 'POST':
        try:
            # Prefer server-side session workflow, but accept JSON/form payloads
            workflow_data = session.get('product_workflow', {}) or {}

            # If session has no workflow, try to parse JSON payload from client
            if not workflow_data:
                payload = request.get_json(silent=True)
                if payload:
                    # Expect payload to contain step1/step2/step3
                    workflow_data = {
                        'step1': payload.get('step1', {}),
                        'step2': payload.get('step2', {}),
                        'step3': payload.get('step3', {}),
                    }
                    # Mirror into session for consistency
                    session['product_workflow'] = workflow_data
                    session.modified = True
                else:
                    # Fallback: try to build from form fields (legacy)
                    # ... (existing form parsing code)
                    pass

            step1 = workflow_data.get('step1', {})
            step2 = workflow_data.get('step2', {})
            step3 = workflow_data.get('step3', {})
            
            # Validate required fields
            product_name = step1.get('productName', '').strip()
            category = step1.get('category', '').strip()
            
            if not product_name or not category:
                flash('Product name and category are required.', 'danger')
                return redirect(url_for('seller.add_product'))
            
            # Validate user authentication (should be handled by before_request, but double-check)
            if not current_user.is_authenticated or current_user.role != 'seller':
                flash('Authentication required to save products.', 'danger')
                return redirect(url_for('auth.login'))
            
            # ... (existing price calculation and product creation code)
            
            try:
                product = SellerProduct(
                    seller_id=current_user.id,
                    # ... (existing product fields)
                )
                
                db.session.add(product)
                db.session.commit()
                
                session.pop('product_workflow', None)
                
                flash('Product added successfully!', 'success')
                return redirect(url_for('seller.seller_products'))
                
            except SQLAlchemyError as exc:
                db.session.rollback()
                current_app.logger.error("Failed to save product: %s", exc)
                flash('Error saving product. Please try again.', 'danger')
                return redirect(url_for('seller.add_product_preview'))
                
        except Exception as e:
            current_app.logger.error("Unexpected error in add_product_preview: %s", e)
            flash('An unexpected error occurred. Please try again.', 'danger')
            return redirect(url_for('seller.add_product_preview'))
    
    workflow_data = session.get('product_workflow', {})
    
    return render_template(
        'seller/add_product_preview.html',
        product_data=workflow_data
    )
'''
    
    print("✓ Route enhancement suggestions prepared")
    
    # Fix 3: Create a user guide for troubleshooting
    user_guide = '''
# Product Creation Troubleshooting Guide

## Common Issues and Solutions

### 1. "Add Product" button not working
**Symptoms:** Clicking the button does nothing or shows an error
**Solutions:**
- Check browser console for JavaScript errors (F12 → Console)
- Verify you're logged in as a seller
- Clear browser cache and cookies
- Try refreshing the page

### 2. "Session expired" or login redirect
**Symptoms:** Redirected to login page when clicking "Add Product"
**Solutions:**
- Log in again with your seller account
- Make sure your account has seller role and is approved
- Check if your session timeout settings

### 3. Product not appearing in product list
**Symptoms:** Success message shown but product not in database
**Solutions:**
- Check if you have proper seller permissions
- Verify database connection
- Check server logs for errors
- Try creating a simple product with minimal data first

### 4. Network or server errors
**Symptoms:** "Network error" or "Server error" messages
**Solutions:**
- Check internet connection
- Verify server is running
- Check server logs for detailed error messages
- Try again after a few minutes

## Debug Steps

1. **Check Authentication:**
   - Verify you're logged in as a seller
   - Check your user role in the database
   - Ensure your seller account is approved

2. **Check Form Data:**
   - Open browser dev tools (F12)
   - Go to Application/Storage -> Local Storage
   - Verify productForm, productDescriptionForm, and productStocksForm contain data

3. **Check Network Requests:**
   - Open browser dev tools (F12) -> Network tab
   - Click "Add Product" and watch for failed requests
   - Check response codes and error messages

4. **Check Server Logs:**
   - Look for error messages in the Flask application logs
   - Check database connection status
   - Verify all required tables exist

## Contact Support

If issues persist, provide the following information:
- Browser console errors (F12 -> Console)
- Network request details (F12 -> Network)
- Steps to reproduce the issue
- Your user account details (email/username)
'''
    
    with open('PRODUCT_CREATION_TROUBLESHOOTING.md', 'w', encoding='utf-8') as f:
        f.write(user_guide)
    
    print("✓ Troubleshooting guide created")
    
    print("\n=== Fixes Applied ===")
    print("1. Enhanced JavaScript with better error handling")
    print("2. Route enhancement suggestions prepared")
    print("3. Troubleshooting guide created")
    print("\n=== Next Steps ===")
    print("1. Update the template to use the enhanced JavaScript")
    print("2. Test the authentication flow")
    print("3. Check browser console for any remaining errors")
    
    return True

if __name__ == '__main__':
    fix_authentication_issues()