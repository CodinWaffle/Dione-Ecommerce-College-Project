#!/usr/bin/env python3
"""
Quick test to verify add variant button and photo upload functionality
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_functionality():
    print("🧪 Testing Add Variant and Photo Upload Functionality...")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome driver initialized")
        
        # Navigate to the page
        print("📂 Opening add_product_stocks page...")
        driver.get("http://localhost:5000/seller/add_product_stocks")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Test 1: Check if Add Variant button exists and is clickable
        print("\n🔍 Test 1: Add Variant Button")
        try:
            add_variant_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "addVariantBtn"))
            )
            print("✅ Add Variant button found and clickable")
            
            # Count initial rows
            initial_rows = driver.find_elements(By.CSS_SELECTOR, "#variantTableBody tr")
            initial_count = len(initial_rows)
            print(f"📊 Initial variant count: {initial_count}")
            
            # Click add variant button
            print("🖱️ Clicking Add Variant button...")
            driver.execute_script("arguments[0].click();", add_variant_btn)
            time.sleep(1)  # Wait for row to be added
            
            # Check if new row was added
            new_rows = driver.find_elements(By.CSS_SELECTOR, "#variantTableBody tr")
            new_count = len(new_rows)
            print(f"📊 New variant count: {new_count}")
            
            if new_count > initial_count:
                print("✅ Add Variant button works! New row added successfully")
            else:
                print("❌ Add Variant button failed - no new row added")
                
        except Exception as e:
            print(f"❌ Add Variant button test failed: {e}")
        
        # Test 2: Check photo upload functionality
        print("\n🔍 Test 2: Photo Upload Boxes")
        try:
            # Find all photo upload boxes
            photo_boxes = driver.find_elements(By.CSS_SELECTOR, ".photo-upload-box")
            print(f"📸 Found {len(photo_boxes)} photo upload boxes")
            
            if photo_boxes:
                # Test clicking the first photo box
                first_box = photo_boxes[0]
                print("🖱️ Testing photo box click...")
                
                # Check if file input exists
                file_inputs = driver.find_elements(By.CSS_SELECTOR, ".photo-upload-box input[type='file']")
                print(f"📁 Found {len(file_inputs)} file inputs")
                
                if file_inputs:
                    print("✅ Photo upload structure is correct")
                else:
                    print("❌ No file inputs found in photo boxes")
                    
            else:
                print("❌ No photo upload boxes found")
                
        except Exception as e:
            print(f"❌ Photo upload test failed: {e}")
            
        # Test 3: Check console for JavaScript errors
        print("\n🔍 Test 3: JavaScript Console")
        try:
            # Get browser console logs
            logs = driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            warnings = [log for log in logs if log['level'] == 'WARNING']
            
            print(f"⚠️ Console warnings: {len(warnings)}")
            print(f"❌ Console errors: {len(errors)}")
            
            if errors:
                print("JavaScript Errors found:")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"  - {error['message']}")
            else:
                print("✅ No serious JavaScript errors found")
                
        except Exception as e:
            print(f"⚠️ Could not check console logs: {e}")
            
        # Test 4: Check if scripts loaded
        print("\n🔍 Test 4: Script Loading")
        try:
            # Check if variant manager console message appears
            script_result = driver.execute_script("""
                return {
                    variantButton: !!document.getElementById('addVariantBtn'),
                    photoBoxes: document.querySelectorAll('.photo-upload-box').length,
                    setupFunction: typeof window.setupPhotoUpload === 'function'
                };
            """)
            
            print(f"🔧 Variant button exists: {script_result['variantButton']}")
            print(f"📸 Photo boxes count: {script_result['photoBoxes']}")
            print(f"🔧 Global setup function: {script_result['setupFunction']}")
            
            if script_result['variantButton'] and script_result['photoBoxes'] > 0:
                print("✅ All key elements are present")
            else:
                print("❌ Some key elements are missing")
                
        except Exception as e:
            print(f"❌ Script loading test failed: {e}")
            
    except Exception as e:
        print(f"❌ Browser setup failed: {e}")
        return False
        
    finally:
        if 'driver' in locals():
            driver.quit()
            print("\n🔧 Browser closed")
    
    print("\n🎯 Test Summary:")
    print("   1. Add Variant Button - Check if it adds new rows")
    print("   2. Photo Upload Boxes - Check if upload structure exists") 
    print("   3. JavaScript Console - Check for errors")
    print("   4. Script Loading - Check if all scripts loaded properly")
    print("\n✅ Testing completed!")
    return True

if __name__ == "__main__":
    test_functionality()