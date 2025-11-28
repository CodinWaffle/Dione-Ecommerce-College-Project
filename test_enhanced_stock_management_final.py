#!/usr/bin/env python3
"""
Enhanced Stock Management Test Suite
Tests the improved inventory management features including bulk operations, validation, and UX enhancements.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None

def test_enhanced_stock_page_load(driver):
    """Test that the enhanced stock management page loads correctly"""
    print("Testing enhanced stock management page load...")
    
    try:
        # Navigate to the stock management page
        driver.get("http://localhost:5000/seller/add_product_stocks")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Check for enhanced header elements
        page_header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "page-header")))
        assert page_header is not None, "Page header not found"
        
        # Check for new action buttons
        bulk_btn = driver.find_element(By.ID, "bulkStockBtn")
        validate_btn = driver.find_element(By.ID, "validateStockBtn")
        
        assert bulk_btn is not None, "Bulk stock button not found"
        assert validate_btn is not None, "Validate stock button not found"
        
        # Check for variant controls
        variant_controls = driver.find_element(By.CLASS_NAME, "variant-controls")
        assert variant_controls is not None, "Variant controls not found"
        
        # Check for stats display
        variant_count = driver.find_element(By.ID, "variantCount")
        total_stock = driver.find_element(By.ID, "totalStockDisplay")
        
        assert variant_count is not None, "Variant count display not found"
        assert total_stock is not None, "Total stock display not found"
        
        print("✓ Enhanced stock management page loaded successfully")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced stock page load test failed: {e}")
        return False

def test_bulk_stock_modal(driver):
    """Test the bulk stock management modal functionality"""
    print("Testing bulk stock modal...")
    
    try:
        # Click bulk stock button
        bulk_btn = driver.find_element(By.ID, "bulkStockBtn")
        bulk_btn.click()
        
        # Wait for modal to appear
        wait = WebDriverWait(driver, 5)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "bulkStockModal")))
        
        # Check modal structure
        modal_header = modal.find_element(By.CLASS_NAME, "modal-header")
        modal_body = modal.find_element(By.CLASS_NAME, "modal-body")
        modal_footer = modal.find_element(By.CLASS_NAME, "modal-footer")
        
        assert modal_header is not None, "Modal header not found"
        assert modal_body is not None, "Modal body not found"
        assert modal_footer is not None, "Modal footer not found"
        
        # Check bulk options
        bulk_options = modal.find_elements(By.CLASS_NAME, "bulk-option")
        assert len(bulk_options) >= 3, "Not enough bulk options found"
        
        # Test radio button functionality
        radio_buttons = modal.find_elements(By.CSS_SELECTOR, 'input[name="bulkType"]')
        assert len(radio_buttons) >= 3, "Not enough radio buttons found"
        
        # Test "by size" option
        by_size_radio = modal.find_element(By.CSS_SELECTOR, 'input[value="bySize"]')
        by_size_radio.click()
        
        # Check if size inputs container appears
        time.sleep(0.5)  # Wait for UI update
        size_inputs = modal.find_element(By.ID, "bulkSizeInputs")
        assert size_inputs.is_displayed(), "Size inputs not displayed when 'by size' selected"
        
        # Close modal
        close_btn = modal.find_element(By.ID, "bulkModalClose")
        close_btn.click()
        
        # Wait for modal to close
        wait.until(EC.invisibility_of_element_located((By.ID, "bulkStockModal")))
        
        print("✓ Bulk stock modal functionality working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Bulk stock modal test failed: {e}")
        return False

def test_validation_modal(driver):
    """Test the stock validation modal functionality"""
    print("Testing validation modal...")
    
    try:
        # Click validate button
        validate_btn = driver.find_element(By.ID, "validateStockBtn")
        validate_btn.click()
        
        # Wait for validation modal to appear
        wait = WebDriverWait(driver, 5)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "validationModal")))
        
        # Check modal structure
        modal_header = modal.find_element(By.CLASS_NAME, "modal-header")
        modal_body = modal.find_element(By.CLASS_NAME, "modal-body")
        
        assert modal_header is not None, "Validation modal header not found"
        assert modal_body is not None, "Validation modal body not found"
        
        # Check for validation results
        validation_results = modal.find_element(By.ID, "validationResults")
        assert validation_results is not None, "Validation results container not found"
        
        # Check for validation sections (should have at least one)
        validation_sections = modal.find_elements(By.CLASS_NAME, "validation-section")
        assert len(validation_sections) > 0, "No validation sections found"
        
        # Close modal
        close_btn = modal.find_element(By.ID, "validationModalClose")
        close_btn.click()
        
        # Wait for modal to close
        wait.until(EC.invisibility_of_element_located((By.ID, "validationModal")))
        
        print("✓ Validation modal functionality working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Validation modal test failed: {e}")
        return False

def test_enhanced_size_selection(driver):
    """Test the enhanced size selection modal"""
    print("Testing enhanced size selection...")
    
    try:
        # Click on "Select Sizes" button
        select_sizes_btn = driver.find_element(By.CLASS_NAME, "btn-select-sizes")
        select_sizes_btn.click()
        
        # Wait for size selection modal
        wait = WebDriverWait(driver, 5)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "sizeSelectModal")))
        
        # Check for enhanced modal structure
        modal_header = modal.find_element(By.CLASS_NAME, "modal-header")
        modal_body = modal.find_element(By.CLASS_NAME, "modal-body")
        modal_footer = modal.find_element(By.CLASS_NAME, "modal-footer")
        
        assert modal_header is not None, "Size modal header not found"
        assert modal_body is not None, "Size modal body not found"
        assert modal_footer is not None, "Size modal footer not found"
        
        # Check for size options
        size_options = modal.find_element(By.ID, "sizeOptionsContainer")
        assert size_options is not None, "Size options container not found"
        
        # Check for size groups
        size_groups = modal.find_elements(By.CLASS_NAME, "size-group-container")
        assert len(size_groups) > 0, "No size groups found"
        
        # Check for custom size section
        custom_section = modal.find_element(By.CLASS_NAME, "custom-size-section")
        assert custom_section is not None, "Custom size section not found"
        
        # Test selecting a size
        size_boxes = modal.find_elements(By.CLASS_NAME, "size-selection-box")
        if size_boxes:
            size_boxes[0].click()
            assert "selected" in size_boxes[0].get_attribute("class"), "Size not selected properly"
        
        # Close modal
        close_btn = modal.find_element(By.ID, "sizeModalClose")
        close_btn.click()
        
        print("✓ Enhanced size selection working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced size selection test failed: {e}")
        return False

def test_variant_stats_update(driver):
    """Test that variant statistics update correctly"""
    print("Testing variant statistics updates...")
    
    try:
        # Get initial variant count
        variant_count_el = driver.find_element(By.ID, "variantCount")
        initial_count = int(variant_count_el.text)
        
        # Get initial total stock
        total_stock_el = driver.find_element(By.ID, "totalStockDisplay")
        initial_stock = int(total_stock_el.text)
        
        # Add some stock to test updates
        stock_inputs = driver.find_elements(By.CLASS_NAME, "size-stock-input")
        if stock_inputs:
            # Add stock to first input
            stock_inputs[0].clear()
            stock_inputs[0].send_keys("10")
            
            # Trigger update (simulate input event)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", stock_inputs[0])
            
            # Wait a moment for update
            time.sleep(0.5)
            
            # Check if total stock updated
            updated_stock = int(total_stock_el.text)
            assert updated_stock >= initial_stock, "Total stock did not update correctly"
        
        print("✓ Variant statistics update correctly")
        return True
        
    except Exception as e:
        print(f"✗ Variant statistics test failed: {e}")
        return False

def test_responsive_design(driver):
    """Test responsive design features"""
    print("Testing responsive design...")
    
    try:
        # Test mobile viewport
        driver.set_window_size(375, 667)  # iPhone SE size
        time.sleep(1)
        
        # Check if page is still functional
        page_header = driver.find_element(By.CLASS_NAME, "page-header")
        variant_controls = driver.find_element(By.CLASS_NAME, "variant-controls")
        
        assert page_header.is_displayed(), "Page header not visible on mobile"
        assert variant_controls.is_displayed(), "Variant controls not visible on mobile"
        
        # Test tablet viewport
        driver.set_window_size(768, 1024)  # iPad size
        time.sleep(1)
        
        # Check functionality
        bulk_btn = driver.find_element(By.ID, "bulkStockBtn")
        assert bulk_btn.is_displayed(), "Bulk button not visible on tablet"
        
        # Reset to desktop
        driver.set_window_size(1920, 1080)
        time.sleep(1)
        
        print("✓ Responsive design working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Responsive design test failed: {e}")
        return False

def test_accessibility_features(driver):
    """Test accessibility features"""
    print("Testing accessibility features...")
    
    try:
        # Check for ARIA labels and roles
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons[:5]:  # Check first 5 buttons
            title = button.get_attribute("title")
            aria_label = button.get_attribute("aria-label")
            # At least one should be present for accessibility
            assert title or aria_label or button.text.strip(), f"Button missing accessibility text: {button.get_attribute('outerHTML')[:100]}"
        
        # Check for proper form labels
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for input_el in inputs[:5]:  # Check first 5 inputs
            input_type = input_el.get_attribute("type")
            if input_type in ["text", "number", "email"]:
                placeholder = input_el.get_attribute("placeholder")
                aria_label = input_el.get_attribute("aria-label")
                # Should have some form of labeling
                assert placeholder or aria_label, f"Input missing accessibility label: {input_el.get_attribute('outerHTML')[:100]}"
        
        print("✓ Accessibility features present")
        return True
        
    except Exception as e:
        print(f"✗ Accessibility test failed: {e}")
        return False

def run_all_tests():
    """Run all enhanced stock management tests"""
    print("🚀 Starting Enhanced Stock Management Test Suite")
    print("=" * 60)
    
    driver = setup_driver()
    if not driver:
        print("❌ Failed to setup driver")
        return False
    
    tests = [
        test_enhanced_stock_page_load,
        test_bulk_stock_modal,
        test_validation_modal,
        test_enhanced_size_selection,
        test_variant_stats_update,
        test_responsive_design,
        test_accessibility_features
    ]
    
    passed = 0
    failed = 0
    
    try:
        for test in tests:
            try:
                if test(driver):
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"✗ Test {test.__name__} failed with exception: {e}")
                failed += 1
            
            print("-" * 40)
    
    finally:
        driver.quit()
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All enhanced stock management tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)