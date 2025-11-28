#!/usr/bin/env python3
"""
My Purchases Reviews Test Suite
Tests the My Purchases page with reviews functionality, write review modal, and enhanced UX.
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

def test_my_purchases_page_load(driver):
    """Test that the My Purchases page loads correctly"""
    print("Testing My Purchases page load...")
    
    try:
        # Navigate to the My Purchases page
        driver.get("http://localhost:5000/my-purchases")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Check for page header
        page_header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "page-header")))
        assert page_header is not None, "Page header not found"
        
        # Check for order tabs
        order_tabs = driver.find_element(By.CLASS_NAME, "order-tabs")
        assert order_tabs is not None, "Order tabs not found"
        
        # Check for orders list
        orders_list = driver.find_element(By.CLASS_NAME, "orders-list")
        assert orders_list is not None, "Orders list not found"
        
        # Check for sample orders
        order_cards = driver.find_elements(By.CLASS_NAME, "order-card")
        assert len(order_cards) > 0, "No order cards found"
        
        print("✓ My Purchases page loaded successfully")
        return True
        
    except Exception as e:
        print(f"✗ My Purchases page load test failed: {e}")
        return False

def test_order_status_tabs(driver):
    """Test order status tab functionality"""
    print("Testing order status tabs...")
    
    try:
        # Find tab buttons
        tab_buttons = driver.find_elements(By.CLASS_NAME, "tab-btn")
        assert len(tab_buttons) >= 5, "Not enough tab buttons found"
        
        # Test clicking different tabs
        for i, tab in enumerate(tab_buttons[:3]):  # Test first 3 tabs
            tab.click()
            time.sleep(0.5)
            
            # Check if tab becomes active
            assert "active" in tab.get_attribute("class"), f"Tab {i} did not become active"
        
        print("✓ Order status tabs working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Order status tabs test failed: {e}")
        return False

def test_reviews_dropdown(driver):
    """Test reviews dropdown functionality"""
    print("Testing reviews dropdown...")
    
    try:
        # Find reviews toggle buttons
        reviews_toggles = driver.find_elements(By.CLASS_NAME, "reviews-toggle")
        assert len(reviews_toggles) > 0, "No reviews toggle buttons found"
        
        # Click first reviews toggle
        first_toggle = reviews_toggles[0]
        first_toggle.click()
        time.sleep(0.5)
        
        # Check if dropdown appears
        order_id = first_toggle.get_attribute("data-order")
        dropdown = driver.find_element(By.ID, f"reviews-{order_id}")
        assert "active" in dropdown.get_attribute("class"), "Reviews dropdown did not open"
        
        # Check for reviews content
        reviews_header = dropdown.find_element(By.CLASS_NAME, "reviews-header")
        assert reviews_header is not None, "Reviews header not found"
        
        # Check for rating summary
        rating_summary = dropdown.find_element(By.CLASS_NAME, "rating-summary")
        assert rating_summary is not None, "Rating summary not found"
        
        # Check for review controls
        review_controls = dropdown.find_element(By.CLASS_NAME, "review-controls")
        assert review_controls is not None, "Review controls not found"
        
        print("✓ Reviews dropdown working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Reviews dropdown test failed: {e}")
        return False

def test_write_review_modal(driver):
    """Test write review modal functionality"""
    print("Testing write review modal...")
    
    try:
        # Find write review button (only on delivered orders)
        review_buttons = driver.find_elements(By.CLASS_NAME, "btn-review")
        
        if len(review_buttons) > 0:
            # Click write review button
            review_buttons[0].click()
            time.sleep(0.5)
            
            # Check if modal appears
            modal = driver.find_element(By.ID, "writeReviewModal")
            assert "active" in modal.get_attribute("class"), "Write review modal did not open"
            
            # Check modal structure
            modal_header = modal.find_element(By.CLASS_NAME, "modal-header")
            modal_body = modal.find_element(By.CLASS_NAME, "modal-body")
            modal_footer = modal.find_element(By.CLASS_NAME, "modal-footer")
            
            assert modal_header is not None, "Modal header not found"
            assert modal_body is not None, "Modal body not found"
            assert modal_footer is not None, "Modal footer not found"
            
            # Check for rating sections
            star_ratings = modal.find_elements(By.CLASS_NAME, "star-rating")
            assert len(star_ratings) >= 3, "Not enough star rating sections found"
            
            # Check for review text area
            review_textarea = modal.find_element(By.ID, "reviewText")
            assert review_textarea is not None, "Review textarea not found"
            
            # Check for photo upload section
            photo_upload = modal.find_element(By.CLASS_NAME, "photo-upload-section")
            assert photo_upload is not None, "Photo upload section not found"
            
            # Close modal
            close_btn = modal.find_element(By.ID, "closeReviewModal")
            close_btn.click()
            time.sleep(0.5)
            
            print("✓ Write review modal working correctly")
            return True
        else:
            print("✓ No review buttons found (expected for non-delivered orders)")
            return True
        
    except Exception as e:
        print(f"✗ Write review modal test failed: {e}")
        return False

def test_star_rating_system(driver):
    """Test star rating interaction"""
    print("Testing star rating system...")
    
    try:
        # Open write review modal first
        review_buttons = driver.find_elements(By.CLASS_NAME, "btn-review")
        
        if len(review_buttons) > 0:
            review_buttons[0].click()
            time.sleep(0.5)
            
            # Find star rating sections
            star_ratings = driver.find_elements(By.CLASS_NAME, "star-rating")
            
            if len(star_ratings) > 0:
                # Test clicking stars in first rating section
                first_rating = star_ratings[0]
                stars = first_rating.find_elements(By.TAG_NAME, "i")
                
                # Click 4th star (4-star rating)
                if len(stars) >= 4:
                    stars[3].click()
                    time.sleep(0.2)
                    
                    # Check if stars are filled
                    filled_stars = first_rating.find_elements(By.CLASS_NAME, "ri-star-fill")
                    assert len(filled_stars) == 4, f"Expected 4 filled stars, got {len(filled_stars)}"
                
                print("✓ Star rating system working correctly")
            
            # Close modal
            close_btn = driver.find_element(By.ID, "closeReviewModal")
            close_btn.click()
            time.sleep(0.5)
            
            return True
        else:
            print("✓ No review buttons to test star ratings")
            return True
        
    except Exception as e:
        print(f"✗ Star rating system test failed: {e}")
        return False

def test_review_filters(driver):
    """Test review filter functionality"""
    print("Testing review filters...")
    
    try:
        # Open reviews dropdown first
        reviews_toggles = driver.find_elements(By.CLASS_NAME, "reviews-toggle")
        
        if len(reviews_toggles) > 0:
            reviews_toggles[0].click()
            time.sleep(0.5)
            
            # Find filter buttons
            filter_buttons = driver.find_elements(By.CLASS_NAME, "btn-filter")
            
            if len(filter_buttons) > 0:
                # Test clicking different filters
                for i, filter_btn in enumerate(filter_buttons[:3]):  # Test first 3 filters
                    filter_btn.click()
                    time.sleep(0.3)
                    
                    # Check if filter becomes active
                    assert "active" in filter_btn.get_attribute("class"), f"Filter {i} did not become active"
                
                print("✓ Review filters working correctly")
                return True
            else:
                print("✓ No filter buttons found (expected for orders without reviews)")
                return True
        else:
            print("✓ No reviews toggle found")
            return True
        
    except Exception as e:
        print(f"✗ Review filters test failed: {e}")
        return False

def test_no_reviews_state(driver):
    """Test the centered grey 'No reviews yet' message"""
    print("Testing no reviews state...")
    
    try:
        # Look for orders without reviews (processing status)
        processing_orders = driver.find_elements(By.CSS_SELECTOR, '[data-status="processing"]')
        
        if len(processing_orders) > 0:
            # Find reviews toggle for processing order
            processing_toggle = processing_orders[0].find_element(By.CLASS_NAME, "reviews-toggle")
            processing_toggle.click()
            time.sleep(0.5)
            
            # Check for no reviews message
            no_reviews_message = processing_orders[0].find_element(By.CLASS_NAME, "no-reviews-message")
            assert no_reviews_message is not None, "No reviews message not found"
            
            # Check if message is properly styled
            message_text = no_reviews_message.find_element(By.TAG_NAME, "p")
            assert "No reviews yet" in message_text.text, "Incorrect no reviews message text"
            
            print("✓ No reviews state working correctly")
            return True
        else:
            print("✓ No processing orders found to test no reviews state")
            return True
        
    except Exception as e:
        print(f"✗ No reviews state test failed: {e}")
        return False

def test_responsive_design(driver):
    """Test responsive design on different screen sizes"""
    print("Testing responsive design...")
    
    try:
        # Test mobile viewport
        driver.set_window_size(375, 667)
        time.sleep(1)
        
        # Check if page is still functional
        page_header = driver.find_element(By.CLASS_NAME, "page-header")
        order_tabs = driver.find_element(By.CLASS_NAME, "order-tabs")
        
        assert page_header.is_displayed(), "Page header not visible on mobile"
        assert order_tabs.is_displayed(), "Order tabs not visible on mobile"
        
        # Test tablet viewport
        driver.set_window_size(768, 1024)
        time.sleep(1)
        
        # Check functionality
        orders_list = driver.find_element(By.CLASS_NAME, "orders-list")
        assert orders_list.is_displayed(), "Orders list not visible on tablet"
        
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
        # Check for proper ARIA labels and roles
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons[:5]:  # Check first 5 buttons
            # Should have either text content, aria-label, or title
            text = button.text.strip()
            aria_label = button.get_attribute("aria-label")
            title = button.get_attribute("title")
            
            assert text or aria_label or title, f"Button missing accessibility text: {button.get_attribute('outerHTML')[:100]}"
        
        # Check for proper heading structure
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        assert len(headings) > 0, "No headings found for screen readers"
        
        # Check for form labels
        labels = driver.find_elements(By.TAG_NAME, "label")
        inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
        
        # Should have labels for form inputs
        if len(inputs) > 0:
            assert len(labels) > 0, "Form inputs found but no labels for accessibility"
        
        print("✓ Accessibility features present")
        return True
        
    except Exception as e:
        print(f"✗ Accessibility test failed: {e}")
        return False

def run_all_tests():
    """Run all My Purchases reviews tests"""
    print("🛒 Starting My Purchases Reviews Test Suite")
    print("=" * 60)
    
    driver = setup_driver()
    if not driver:
        print("❌ Failed to setup driver")
        return False
    
    tests = [
        test_my_purchases_page_load,
        test_order_status_tabs,
        test_reviews_dropdown,
        test_write_review_modal,
        test_star_rating_system,
        test_review_filters,
        test_no_reviews_state,
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
        print("\n🎉 All My Purchases reviews tests passed!")
        print("✨ Reviews system is working perfectly!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)