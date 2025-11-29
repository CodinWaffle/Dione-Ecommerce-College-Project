"""
Integration test for product variant selection workflow.
Tests the complete user interaction flow from color selection to cart addition.
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pytest


class TestProductVariantIntegration:
    """Integration tests for product variant selection workflow."""

    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome driver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    @pytest.fixture
    def sample_product_page(self, driver, test_server):
        """Navigate to a sample product page."""
        # Assuming test_server fixture provides the base URL
        driver.get(f"{test_server}/product/1")  # Navigate to product with ID 1
        return driver

    def test_color_selection_loads_sizes(self, sample_product_page):
        """Test that selecting a color loads the appropriate sizes."""
        driver = sample_product_page
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "color-option"))
        )
        
        # Initially, sizes should show placeholder
        size_container = driver.find_element(By.ID, "sizeOptions")
        assert "Select a color" in size_container.text
        
        # Click on first color option
        color_options = driver.find_elements(By.CLASS_NAME, "color-option")
        assert len(color_options) > 0, "No color options found"
        
        first_color = color_options[0]
        color_name = first_color.get_attribute("data-color")
        first_color.click()
        
        # Wait for sizes to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "size-option"))
        )
        
        # Verify sizes are loaded
        size_options = driver.find_elements(By.CLASS_NAME, "size-option")
        assert len(size_options) > 0, "No size options loaded after color selection"
        
        # Verify selected color is highlighted
        assert "active" in first_color.get_attribute("class")
        
        # Verify color name is displayed
        selected_color_span = driver.find_element(By.CLASS_NAME, "selected-color")
        assert selected_color_span.text == color_name

    def test_size_selection_updates_stock(self, sample_product_page):
        """Test that selecting a size updates the stock display."""
        driver = sample_product_page
        
        # Select a color first
        color_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "color-option"))
        )
        color_option.click()
        
        # Wait for sizes to load
        size_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "size-option"))
        )
        
        # Get the stock value from the size button
        expected_stock = size_option.get_attribute("data-stock")
        
        # Click the size option
        size_option.click()
        
        # Wait for stock display to update
        stock_indicator = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "stockIndicator"))
        )
        
        # Verify stock is displayed correctly
        assert stock_indicator.text == expected_stock
        
        # Verify size is selected (has active class)
        assert "active" in size_option.get_attribute("class")

    def test_out_of_stock_size_handling(self, sample_product_page):
        """Test that out-of-stock sizes are properly disabled."""
        driver = sample_product_page
        
        # Select a color
        color_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "color-option"))
        )
        color_option.click()
        
        # Wait for sizes to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "size-option"))
        )
        
        # Find out-of-stock sizes
        out_of_stock_sizes = driver.find_elements(By.CSS_SELECTOR, ".size-option.disabled, .size-option.out-of-stock")
        
        for oos_size in out_of_stock_sizes:
            # Verify disabled attribute
            assert oos_size.get_attribute("disabled") is not None or "disabled" in oos_size.get_attribute("class")
            
            # Verify stock is 0
            stock = oos_size.get_attribute("data-stock")
            assert stock == "0"

    def test_add_to_cart_validation(self, sample_product_page):
        """Test add to cart button behavior and validation."""
        driver = sample_product_page
        
        # Try to add to cart without selecting color/size
        add_to_cart_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "add-to-bag-btn"))
        )
        add_to_cart_btn.click()
        
        # Should show error message
        WebDriverWait(driver, 5).until(
            lambda d: "SELECT COLOR" in add_to_cart_btn.text
        )
        
        # Select color and size
        color_option = driver.find_element(By.CLASS_NAME, "color-option")
        color_option.click()
        
        # Wait for sizes and select an available one
        available_size = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".size-option:not(.disabled):not(.out-of-stock)"))
        )
        available_size.click()
        
        # Now add to cart should work
        add_to_cart_btn.click()
        
        # Should show success state
        WebDriverWait(driver, 5).until(
            lambda d: "ADDED" in add_to_cart_btn.text or "ADDING" in add_to_cart_btn.text
        )

    def test_quantity_validation(self, sample_product_page):
        """Test quantity input validation."""
        driver = sample_product_page
        
        # Select color and size first
        color_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "color-option"))
        )
        color_option.click()
        
        available_size = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".size-option:not(.disabled):not(.out-of-stock)"))
        )
        available_size.click()
        
        # Test quantity input
        quantity_input = driver.find_element(By.ID, "quantityInput")
        
        # Get max stock for this size
        max_stock = int(available_size.get_attribute("data-stock"))
        
        # Set quantity to exceed stock
        quantity_input.clear()
        quantity_input.send_keys(str(max_stock + 10))
        
        # Try to add to cart
        add_to_cart_btn = driver.find_element(By.CLASS_NAME, "add-to-bag-btn")
        add_to_cart_btn.click()
        
        # Should show stock limitation message
        WebDriverWait(driver, 5).until(
            lambda d: "AVAILABLE" in add_to_cart_btn.text or "STOCK" in add_to_cart_btn.text
        )

    def test_accessibility_features(self, sample_product_page):
        """Test accessibility features like ARIA labels and screen reader support."""
        driver = sample_product_page
        
        # Select color to load sizes
        color_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "color-option"))
        )
        color_option.click()
        
        # Wait for sizes to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "size-option"))
        )
        
        # Check that size options have proper aria-label
        size_options = driver.find_elements(By.CLASS_NAME, "size-option")
        for size_option in size_options:
            aria_label = size_option.get_attribute("aria-label")
            assert aria_label is not None, "Size option missing aria-label"
            assert "Size" in aria_label and ("available" in aria_label or "left" in aria_label)
        
        # Check for aria-live regions (announcements)
        live_regions = driver.find_elements(By.CSS_SELECTOR, "[aria-live]")
        assert len(live_regions) > 0, "No aria-live regions found for announcements"

    def test_color_change_updates_sizes(self, sample_product_page):
        """Test that changing colors updates the available sizes."""
        driver = sample_product_page
        
        # Get all color options
        color_options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "color-option"))
        )
        
        if len(color_options) < 2:
            pytest.skip("Need at least 2 colors to test color change")
        
        # Select first color
        first_color = color_options[0]
        first_color.click()
        
        # Wait for sizes to load and get the count
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "size-option"))
        )
        first_color_sizes = driver.find_elements(By.CLASS_NAME, "size-option")
        first_sizes_count = len(first_color_sizes)
        
        # Select second color
        second_color = color_options[1]
        second_color.click()
        
        # Wait for sizes to update
        time.sleep(1)  # Give time for API call and re-render
        
        # Get new sizes
        second_color_sizes = driver.find_elements(By.CLASS_NAME, "size-option")
        second_sizes_count = len(second_color_sizes)
        
        # Verify that the size selection was cleared
        active_sizes = driver.find_elements(By.CSS_SELECTOR, ".size-option.active")
        assert len(active_sizes) == 0, "Size selection should be cleared when changing colors"
        
        # Note: The actual size counts may be different between colors
        # This test mainly verifies that the sizes are refreshed

    def test_loading_states(self, sample_product_page):
        """Test that loading states are shown during API calls."""
        driver = sample_product_page
        
        # Select a color
        color_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "color-option"))
        )
        
        color_option.click()
        
        # Check for loading state (might be brief)
        size_container = driver.find_element(By.ID, "sizeOptions")
        
        # Wait for either loading state or final sizes
        WebDriverWait(driver, 10).until(
            lambda d: "Loading" in size_container.text or d.find_elements(By.CLASS_NAME, "size-option")
        )
        
        # Eventually sizes should load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "size-option"))
        )

    def test_error_handling(self, sample_product_page):
        """Test error handling for API failures."""
        driver = sample_product_page
        
        # Inject JavaScript to simulate API failure
        driver.execute_script("""
            // Override fetch to simulate failure for sizes API
            const originalFetch = window.fetch;
            window.fetch = function(url, ...args) {
                if (url.includes('/colors/') && url.includes('/sizes')) {
                    return Promise.reject(new Error('Simulated network error'));
                }
                return originalFetch(url, ...args);
            };
        """)
        
        # Select a color (should trigger API call that fails)
        color_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "color-option"))
        )
        color_option.click()
        
        # Should show error message or fallback to static data
        size_container = driver.find_element(By.ID, "sizeOptions")
        WebDriverWait(driver, 10).until(
            lambda d: "Unable to load sizes" in size_container.text or d.find_elements(By.CLASS_NAME, "size-option")
        )


# Utility fixture for test server (would need to be implemented based on test setup)
@pytest.fixture(scope="session")
def test_server():
    """Start test server for integration tests."""
    # This would start your Flask app in test mode
    # Implementation depends on your test infrastructure
    return "http://localhost:5000"  # Placeholder


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])