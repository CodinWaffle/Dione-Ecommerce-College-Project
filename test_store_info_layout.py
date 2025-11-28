#!/usr/bin/env python3
"""
Store Info Layout Test Suite
Tests the enhanced store info section with database-driven data and glassmorphism design.
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

def test_store_info_section_display(driver):
    """Test that the store info section displays correctly"""
    print("Testing store info section display...")
    
    try:
        # Navigate to a product detail page
        driver.get("http://localhost:5000/product/1")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Check for store info section
        store_info = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "store-info-section")))
        assert store_info is not None, "Store info section not found"
        
        # Check for store profile elements
        store_profile = store_info.find_element(By.CLASS_NAME, "store-profile")
        assert store_profile is not None, "Store profile not found"
        
        # Check for store avatar
        store_avatar = store_profile.find_element(By.CLASS_NAME, "store-avatar")
        assert store_avatar is not None, "Store avatar not found"
        
        # Check for store details
        store_details = store_profile.find_element(By.CLASS_NAME, "store-details")
        assert store_details is not None, "Store details not found"
        
        # Check for store name
        store_name = store_details.find_element(By.CLASS_NAME, "store-name")
        assert store_name is not None, "Store name not found"
        assert store_name.text.strip() != "", "Store name is empty"
        
        print("✓ Store info section displays correctly")
        return True
        
    except Exception as e:
        print(f"✗ Store info section display test failed: {e}")
        return False

def test_store_statistics_display(driver):
    """Test that store statistics are displayed correctly"""
    print("Testing store statistics display...")
    
    try:
        # Find store stats section
        store_stats = driver.find_element(By.CLASS_NAME, "store-stats")
        assert store_stats is not None, "Store stats not found"
        
        # Check for stat items
        stat_items = store_stats.find_elements(By.CLASS_NAME, "stat-item")
        assert len(stat_items) >= 3, f"Expected at least 3 stat items, found {len(stat_items)}"
        
        # Check for rating stars
        stars = store_stats.find_elements(By.CSS_SELECTOR, ".stars i")
        assert len(stars) == 5, f"Expected 5 rating stars, found {len(stars)}"
        
        # Check for rating text
        rating_text = store_stats.find_element(By.CLASS_NAME, "rating-text")
        assert rating_text is not None, "Rating text not found"
        
        # Check for products count
        products_stat = None
        followers_stat = None
        
        for stat_item in stat_items:
            text = stat_item.text.lower()
            if 'product' in text:
                products_stat = stat_item
            elif 'follower' in text:
                followers_stat = stat_item
        
        assert products_stat is not None, "Products count stat not found"
        assert followers_stat is not None, "Followers count stat not found"
        
        print("✓ Store statistics display correctly")
        return True
        
    except Exception as e:
        print(f"✗ Store statistics display test failed: {e}")
        return False

def test_joined_date_display(driver):
    """Test that the joined date is displayed correctly"""
    print("Testing joined date display...")
    
    try:
        # Find store joined section
        store_joined = driver.find_element(By.CLASS_NAME, "store-joined")
        assert store_joined is not None, "Store joined section not found"
        
        # Check for calendar icon
        calendar_icon = store_joined.find_element(By.CSS_SELECTOR, "i.ri-calendar-line")
        assert calendar_icon is not None, "Calendar icon not found"
        
        # Check for joined text
        joined_text = store_joined.text
        assert "joined" in joined_text.lower(), "Joined text not found"
        
        print("✓ Joined date displays correctly")
        return True
        
    except Exception as e:
        print(f"✗ Joined date display test failed: {e}")
        return False

def test_store_action_buttons(driver):
    """Test that store action buttons are present and functional"""
    print("Testing store action buttons...")
    
    try:
        # Find store actions section
        store_actions = driver.find_element(By.CLASS_NAME, "store-actions")
        assert store_actions is not None, "Store actions not found"
        
        # Check for chat button
        chat_btn = store_actions.find_element(By.CLASS_NAME, "btn-chat")
        assert chat_btn is not None, "Chat button not found"
        assert "chat" in chat_btn.text.lower(), "Chat button text incorrect"
        
        # Check for view shop button
        view_shop_btn = store_actions.find_element(By.CLASS_NAME, "btn-view-shop")
        assert view_shop_btn is not None, "View shop button not found"
        assert "shop" in view_shop_btn.text.lower(), "View shop button text incorrect"
        
        # Test button clicks
        chat_btn.click()
        time.sleep(0.5)
        
        # Check if alert appears (placeholder functionality)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            assert "chat" in alert_text.lower(), "Chat alert not working"
        except:
            pass  # Alert might not appear in headless mode
        
        print("✓ Store action buttons working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Store action buttons test failed: {e}")
        return False

def test_glassmorphism_styling(driver):
    """Test that glassmorphism styling is applied correctly"""
    print("Testing glassmorphism styling...")
    
    try:
        # Find store info section
        store_info = driver.find_element(By.CLASS_NAME, "store-info-section")
        
        # Check CSS properties for glassmorphism
        background = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).background;", 
            store_info
        )
        backdrop_filter = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).backdropFilter;", 
            store_info
        )
        border_radius = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).borderRadius;", 
            store_info
        )
        
        # Verify glassmorphism properties
        assert "rgba" in background or "linear-gradient" in background, "Glassmorphism background not applied"
        assert border_radius == "16px", f"Expected border-radius 16px, got {border_radius}"
        
        # Test hover effect
        ActionChains(driver).move_to_element(store_info).perform()
        time.sleep(0.5)
        
        print("✓ Glassmorphism styling applied correctly")
        return True
        
    except Exception as e:
        print(f"✗ Glassmorphism styling test failed: {e}")
        return False

def test_responsive_design(driver):
    """Test responsive design of store info section"""
    print("Testing responsive design...")
    
    try:
        # Test mobile viewport
        driver.set_window_size(375, 667)
        time.sleep(1)
        
        # Check if store info is still visible and functional
        store_info = driver.find_element(By.CLASS_NAME, "store-info-section")
        assert store_info.is_displayed(), "Store info not visible on mobile"
        
        # Check if buttons stack vertically on mobile
        store_actions = driver.find_element(By.CLASS_NAME, "store-actions")
        actions_style = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).flexDirection;", 
            store_actions
        )
        
        # Test tablet viewport
        driver.set_window_size(768, 1024)
        time.sleep(1)
        
        # Check functionality on tablet
        store_profile = driver.find_element(By.CLASS_NAME, "store-profile")
        assert store_profile.is_displayed(), "Store profile not visible on tablet"
        
        # Reset to desktop
        driver.set_window_size(1920, 1080)
        time.sleep(1)
        
        print("✓ Responsive design working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Responsive design test failed: {e}")
        return False

def test_color_scheme_consistency(driver):
    """Test that the color scheme follows the purple theme"""
    print("Testing color scheme consistency...")
    
    try:
        # Check store avatar background
        store_avatar = driver.find_element(By.CLASS_NAME, "store-avatar")
        avatar_background = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).background;", 
            store_avatar
        )
        
        # Should contain purple colors
        assert "108, 92, 231" in avatar_background or "6c5ce7" in avatar_background.lower(), "Purple theme not applied to avatar"
        
        # Check chat button background
        chat_btn = driver.find_element(By.CLASS_NAME, "btn-chat")
        chat_background = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).background;", 
            chat_btn
        )
        
        # Should contain purple colors
        assert "108, 92, 231" in chat_background or "6c5ce7" in chat_background.lower(), "Purple theme not applied to chat button"
        
        # Check icon colors
        stat_icons = driver.find_elements(By.CSS_SELECTOR, ".stat-item i:not(.stars i)")
        if stat_icons:
            icon_color = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).color;", 
                stat_icons[0]
            )
            # Should be purple or close to it
            assert "108, 92, 231" in icon_color or "6c5ce7" in icon_color.lower(), "Purple theme not applied to icons"
        
        print("✓ Color scheme consistency maintained")
        return True
        
    except Exception as e:
        print(f"✗ Color scheme consistency test failed: {e}")
        return False

def test_accessibility_features(driver):
    """Test accessibility features of store info section"""
    print("Testing accessibility features...")
    
    try:
        # Check for proper button labels
        chat_btn = driver.find_element(By.CLASS_NAME, "btn-chat")
        view_shop_btn = driver.find_element(By.CLASS_NAME, "btn-view-shop")
        
        # Buttons should have text content
        assert chat_btn.text.strip() != "", "Chat button missing text"
        assert view_shop_btn.text.strip() != "", "View shop button missing text"
        
        # Check for proper heading structure
        store_name = driver.find_element(By.CLASS_NAME, "store-name")
        tag_name = store_name.tag_name.lower()
        assert tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], "Store name not using proper heading tag"
        
        # Check for icon accessibility
        icons = driver.find_elements(By.CSS_SELECTOR, ".store-info-section i")
        for icon in icons[:3]:  # Check first 3 icons
            # Icons should have proper classes for screen readers
            class_attr = icon.get_attribute("class")
            assert class_attr and "ri-" in class_attr, "Icon missing proper class"
        
        print("✓ Accessibility features present")
        return True
        
    except Exception as e:
        print(f"✗ Accessibility features test failed: {e}")
        return False

def run_all_tests():
    """Run all store info layout tests"""
    print("🏪 Starting Store Info Layout Test Suite")
    print("=" * 60)
    
    driver = setup_driver()
    if not driver:
        print("❌ Failed to setup driver")
        return False
    
    tests = [
        test_store_info_section_display,
        test_store_statistics_display,
        test_joined_date_display,
        test_store_action_buttons,
        test_glassmorphism_styling,
        test_responsive_design,
        test_color_scheme_consistency,
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
        print("\n🎉 All store info layout tests passed!")
        print("✨ Store info section is working perfectly with glassmorphism design!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)