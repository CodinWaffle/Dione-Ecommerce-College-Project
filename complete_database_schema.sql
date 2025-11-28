-- =============================================================================
-- DIONE ECOMMERCE COMPLETE DATABASE SCHEMA
-- =============================================================================
-- This file contains the complete SQL schema for the entire Dione Ecommerce project
-- Including all tables for users, products, orders, payments, and system management
-- Database: MySQL/MariaDB
-- =============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS dione_ecommerce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dione_ecommerce;

-- =============================================================================
-- USER MANAGEMENT TABLES
-- =============================================================================

-- Main users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255),
    username VARCHAR(150),
    role VARCHAR(20) NOT NULL DEFAULT 'buyer',
    role_requested VARCHAR(20),
    is_approved BOOLEAN NOT NULL DEFAULT TRUE,
    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires DATETIME,
    last_login DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role),
    INDEX idx_user_created_at (created_at)
);

-- OAuth authentication table
CREATE TABLE oauth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(256) NOT NULL,
    provider_user_login VARCHAR(256),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_provider_user (provider, provider_user_id),
    INDEX idx_oauth_user_id (user_id)
);

-- Buyer profiles
CREATE TABLE buyers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(10),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    country VARCHAR(100),
    preferred_language VARCHAR(50) DEFAULT 'English',
    marketing_emails BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_buyer_user_id (user_id)
);

-- Seller profiles
CREATE TABLE sellers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100),
    business_description TEXT,
    business_address TEXT,
    business_city VARCHAR(100),
    business_state VARCHAR(100),
    business_zip VARCHAR(20),
    business_country VARCHAR(100),
    business_phone VARCHAR(20),
    tax_id VARCHAR(50),
    vat_number VARCHAR(50),
    bank_name VARCHAR(255),
    bank_account VARCHAR(100),
    bank_routing VARCHAR(50),
    bank_holder_name VARCHAR(255),
    paypal_email VARCHAR(100),
    store_logo VARCHAR(500),
    store_banner VARCHAR(500),
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_date DATETIME,
    commission_rate DECIMAL(5,2) DEFAULT 5.00,
    total_sales DECIMAL(12,2) DEFAULT 0.00,
    total_orders INT DEFAULT 0,
    rating FLOAT DEFAULT 0.0,
    total_reviews INT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_seller_user_id (user_id),
    INDEX idx_seller_verified (is_verified),
    INDEX idx_seller_rating (rating)
);

-- Rider/Delivery personnel profiles
CREATE TABLE riders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    license_number VARCHAR(50),
    license_expiry DATE,
    vehicle_type VARCHAR(50),
    vehicle_number VARCHAR(50),
    vehicle_model VARCHAR(100),
    availability_status VARCHAR(20) DEFAULT 'available',
    current_latitude DECIMAL(10, 8),
    current_longitude DECIMAL(11, 8),
    delivery_zones TEXT,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_date DATETIME,
    background_check_status VARCHAR(50),
    rating FLOAT DEFAULT 0.0,
    total_deliveries INT DEFAULT 0,
    earnings DECIMAL(10,2) DEFAULT 0.00,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_rider_user_id (user_id),
    INDEX idx_rider_status (availability_status),
    INDEX idx_rider_verified (is_verified),
    INDEX idx_rider_location (current_latitude, current_longitude)
);

-- =============================================================================
-- PRODUCT MANAGEMENT TABLES
-- =============================================================================

-- Product categories
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id INT,
    image VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_category_slug (slug),
    INDEX idx_category_parent (parent_id),
    INDEX idx_category_active (is_active)
);

-- Product brands
CREATE TABLE brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    logo VARCHAR(500),
    website VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_brand_slug (slug),
    INDEX idx_brand_active (is_active)
);

-- Main products table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    short_description TEXT,
    category_id INT,
    subcategory_id INT,
    brand_id INT,
    sku VARCHAR(100),
    barcode VARCHAR(100),
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    compare_at_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    weight DECIMAL(8,2),
    dimensions JSON, -- {length, width, height, unit}
    tax_class VARCHAR(50) DEFAULT 'standard',
    status VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft, active, inactive, archived
    visibility VARCHAR(20) DEFAULT 'public', -- public, private, password_protected
    featured BOOLEAN DEFAULT FALSE,
    allow_backorder BOOLEAN DEFAULT FALSE,
    track_inventory BOOLEAN DEFAULT TRUE,
    manage_stock BOOLEAN DEFAULT TRUE,
    stock_status VARCHAR(20) DEFAULT 'in_stock', -- in_stock, out_of_stock, on_backorder
    low_stock_threshold INT DEFAULT 5,
    image VARCHAR(500),
    gallery JSON, -- Array of image URLs
    tags TEXT,
    meta_title VARCHAR(255),
    meta_description TEXT,
    meta_keywords TEXT,
    attributes JSON, -- Custom product attributes
    variants JSON, -- Product variants summary
    total_stock INT DEFAULT 0,
    total_sold INT DEFAULT 0,
    views INT DEFAULT 0,
    rating FLOAT DEFAULT 0.0,
    review_count INT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (subcategory_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL,
    UNIQUE KEY unique_seller_sku (seller_id, sku),
    INDEX idx_product_seller (seller_id),
    INDEX idx_product_category (category_id),
    INDEX idx_product_brand (brand_id),
    INDEX idx_product_status (status),
    INDEX idx_product_featured (featured),
    INDEX idx_product_price (price),
    INDEX idx_product_stock (total_stock),
    INDEX idx_product_rating (rating),
    INDEX idx_product_created (created_at),
    FULLTEXT idx_product_search (name, description, tags)
);

-- Product variants (colors, sizes, etc.)
CREATE TABLE product_variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255), -- Variant name like "Red - Large"
    color VARCHAR(100),
    color_code VARCHAR(7), -- Hex color code
    size VARCHAR(50),
    material VARCHAR(100),
    style VARCHAR(100),
    price_adjustment DECIMAL(10,2) DEFAULT 0.00,
    compare_at_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    weight DECIMAL(8,2),
    barcode VARCHAR(100),
    image VARCHAR(500),
    position INT DEFAULT 0,
    low_stock_threshold INT DEFAULT 5,
    track_inventory BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_variant_sku (sku),
    INDEX idx_variant_product (product_id),
    INDEX idx_variant_sku (sku),
    INDEX idx_variant_color (color),
    INDEX idx_variant_size (size)
);

-- Product stock levels (inventory tracking)
CREATE TABLE product_stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    variant_id INT NOT NULL,
    size VARCHAR(50) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    reserved_quantity INT DEFAULT 0, -- Stock reserved for pending orders
    incoming_quantity INT DEFAULT 0, -- Expected stock from suppliers
    location VARCHAR(100) DEFAULT 'default', -- Warehouse/location
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE CASCADE,
    UNIQUE KEY unique_variant_size_location (variant_id, size, location),
    INDEX idx_stock_variant (variant_id),
    INDEX idx_stock_quantity (stock_quantity)
);

-- Product images/media
CREATE TABLE product_media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    variant_id INT,
    type VARCHAR(20) NOT NULL, -- image, video, document
    url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    title VARCHAR(255),
    position INT DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE CASCADE,
    INDEX idx_media_product (product_id),
    INDEX idx_media_variant (variant_id),
    INDEX idx_media_type (type),
    INDEX idx_media_position (position)
);

-- =============================================================================
-- ORDER MANAGEMENT TABLES
-- =============================================================================

-- Shopping carts
CREATE TABLE carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    session_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_cart_user (user_id),
    INDEX idx_cart_session (session_id)
);

-- Cart items
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE SET NULL,
    INDEX idx_cart_item_cart (cart_id),
    INDEX idx_cart_item_product (product_id)
);

-- Orders
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    user_id INT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, processing, shipped, delivered, cancelled, refunded
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, paid, failed, refunded, partial
    currency VARCHAR(3) DEFAULT 'USD',
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    shipping_amount DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    
    -- Billing information
    billing_first_name VARCHAR(100),
    billing_last_name VARCHAR(100),
    billing_company VARCHAR(200),
    billing_address_1 VARCHAR(255),
    billing_address_2 VARCHAR(255),
    billing_city VARCHAR(100),
    billing_state VARCHAR(100),
    billing_zip VARCHAR(20),
    billing_country VARCHAR(100),
    billing_phone VARCHAR(20),
    billing_email VARCHAR(100),
    
    -- Shipping information
    shipping_first_name VARCHAR(100),
    shipping_last_name VARCHAR(100),
    shipping_company VARCHAR(200),
    shipping_address_1 VARCHAR(255),
    shipping_address_2 VARCHAR(255),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    shipping_zip VARCHAR(20),
    shipping_country VARCHAR(100),
    shipping_phone VARCHAR(20),
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(100),
    
    notes TEXT,
    processed_at DATETIME,
    shipped_at DATETIME,
    delivered_at DATETIME,
    cancelled_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_order_user (user_id),
    INDEX idx_order_status (status),
    INDEX idx_order_payment_status (payment_status),
    INDEX idx_order_number (order_number),
    INDEX idx_order_created (created_at)
);

-- Order items
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT,
    seller_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    variant_name VARCHAR(255),
    sku VARCHAR(100),
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE SET NULL,
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE RESTRICT,
    INDEX idx_order_item_order (order_id),
    INDEX idx_order_item_product (product_id),
    INDEX idx_order_item_seller (seller_id)
);

-- =============================================================================
-- PAYMENT TABLES
-- =============================================================================

-- Payment methods
CREATE TABLE payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(20) NOT NULL, -- card, bank_account, paypal, etc.
    provider VARCHAR(50), -- stripe, paypal, razorpay, etc.
    provider_id VARCHAR(255), -- External provider ID
    is_default BOOLEAN DEFAULT FALSE,
    last_four VARCHAR(4),
    brand VARCHAR(20), -- visa, mastercard, amex, etc.
    expires_month INT,
    expires_year INT,
    holder_name VARCHAR(255),
    billing_address JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_payment_method_user (user_id),
    INDEX idx_payment_method_default (is_default)
);

-- Payment transactions
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method_id INT,
    transaction_id VARCHAR(255),
    provider VARCHAR(50), -- stripe, paypal, razorpay
    provider_transaction_id VARCHAR(255),
    type VARCHAR(20) NOT NULL, -- payment, refund, partial_refund
    status VARCHAR(20) NOT NULL, -- pending, completed, failed, cancelled
    currency VARCHAR(3) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    fee DECIMAL(10,2) DEFAULT 0.00,
    gateway_response JSON,
    failure_reason TEXT,
    processed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id) ON DELETE SET NULL,
    INDEX idx_payment_order (order_id),
    INDEX idx_payment_status (status),
    INDEX idx_payment_provider (provider),
    INDEX idx_payment_created (created_at)
);

-- =============================================================================
-- REVIEW AND RATING TABLES
-- =============================================================================

-- Product reviews
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    variant_id INT,
    user_id INT NOT NULL,
    order_item_id INT,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    pros TEXT,
    cons TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    helpful_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE SET NULL,
    INDEX idx_review_product (product_id),
    INDEX idx_review_user (user_id),
    INDEX idx_review_rating (rating),
    INDEX idx_review_approved (is_approved)
);

-- Review helpfulness votes
CREATE TABLE review_votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    user_id INT NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_review_user_vote (review_id, user_id)
);

-- =============================================================================
-- SHIPPING AND DELIVERY TABLES
-- =============================================================================

-- Shipping zones
CREATE TABLE shipping_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    countries TEXT, -- JSON array of country codes
    states TEXT, -- JSON array of state/region codes
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_shipping_zone_active (is_active)
);

-- Shipping methods
CREATE TABLE shipping_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type VARCHAR(20) NOT NULL, -- flat_rate, weight_based, free_shipping
    cost DECIMAL(10,2) DEFAULT 0.00,
    min_amount DECIMAL(10,2), -- Minimum order amount for this method
    max_weight DECIMAL(8,2), -- Maximum weight for this method
    estimated_days VARCHAR(20), -- "2-5 business days"
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (zone_id) REFERENCES shipping_zones(id) ON DELETE CASCADE,
    INDEX idx_shipping_method_zone (zone_id),
    INDEX idx_shipping_method_active (is_active)
);

-- Delivery assignments
CREATE TABLE deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    rider_id INT,
    status VARCHAR(20) DEFAULT 'assigned', -- assigned, picked_up, in_transit, delivered, failed
    pickup_address TEXT,
    pickup_latitude DECIMAL(10, 8),
    pickup_longitude DECIMAL(11, 8),
    delivery_address TEXT,
    delivery_latitude DECIMAL(10, 8),
    delivery_longitude DECIMAL(11, 8),
    estimated_pickup_time DATETIME,
    estimated_delivery_time DATETIME,
    actual_pickup_time DATETIME,
    actual_delivery_time DATETIME,
    delivery_notes TEXT,
    delivery_proof VARCHAR(500), -- Photo/signature URL
    customer_rating INT CHECK (customer_rating >= 1 AND customer_rating <= 5),
    customer_feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (rider_id) REFERENCES riders(id) ON DELETE SET NULL,
    INDEX idx_delivery_order (order_id),
    INDEX idx_delivery_rider (rider_id),
    INDEX idx_delivery_status (status)
);

-- =============================================================================
-- COUPON AND DISCOUNT TABLES
-- =============================================================================

-- Coupons and discount codes
CREATE TABLE coupons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255),
    description TEXT,
    type VARCHAR(20) NOT NULL, -- percentage, fixed_amount, free_shipping
    value DECIMAL(10,2) NOT NULL,
    minimum_amount DECIMAL(10,2), -- Minimum order amount
    maximum_discount DECIMAL(10,2), -- Maximum discount amount (for percentage)
    usage_limit INT, -- Total usage limit
    usage_limit_per_customer INT,
    used_count INT DEFAULT 0,
    starts_at DATETIME,
    expires_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_coupon_code (code),
    INDEX idx_coupon_active (is_active),
    INDEX idx_coupon_expires (expires_at)
);

-- Coupon usage tracking
CREATE TABLE coupon_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    coupon_id INT NOT NULL,
    user_id INT,
    order_id INT NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_coupon_usage_coupon (coupon_id),
    INDEX idx_coupon_usage_user (user_id)
);

-- =============================================================================
-- WISHLIST AND FAVORITES
-- =============================================================================

-- User wishlists
CREATE TABLE wishlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE SET NULL,
    UNIQUE KEY unique_user_product_variant (user_id, product_id, variant_id),
    INDEX idx_wishlist_user (user_id),
    INDEX idx_wishlist_product (product_id)
);

-- =============================================================================
-- SYSTEM AND ADMIN TABLES
-- =============================================================================

-- Site settings
CREATE TABLE site_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'text', -- text, number, boolean, json
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (setting_key)
);

-- Admin notifications
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSON, -- Additional data
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notification_user (user_id),
    INDEX idx_notification_read (is_read),
    INDEX idx_notification_created (created_at)
);

-- System logs
CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(10) NOT NULL, -- error, warning, info, debug
    message TEXT NOT NULL,
    context JSON, -- Additional context data
    user_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_log_level (level),
    INDEX idx_log_user (user_id),
    INDEX idx_log_created (created_at)
);

-- Support tickets
CREATE TABLE support_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, in_progress, resolved, closed
    priority VARCHAR(10) DEFAULT 'medium', -- low, medium, high, urgent
    category VARCHAR(50),
    assigned_to INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_ticket_user (user_id),
    INDEX idx_ticket_status (status),
    INDEX idx_ticket_assigned (assigned_to)
);

-- Support ticket messages
CREATE TABLE ticket_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    is_staff_reply BOOLEAN DEFAULT FALSE,
    attachments JSON, -- Array of attachment URLs
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES support_tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_ticket_message_ticket (ticket_id),
    INDEX idx_ticket_message_created (created_at)
);

-- =============================================================================
-- ANALYTICS AND REPORTING TABLES
-- =============================================================================

-- Product views tracking
CREATE TABLE product_views (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT,
    session_id VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_product_view_product (product_id),
    INDEX idx_product_view_user (user_id),
    INDEX idx_product_view_created (created_at)
);

-- Search queries tracking
CREATE TABLE search_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query VARCHAR(255) NOT NULL,
    results_count INT DEFAULT 0,
    user_id INT,
    session_id VARCHAR(255),
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_search_query (query),
    INDEX idx_search_user (user_id),
    INDEX idx_search_created (created_at)
);

-- =============================================================================
-- INSERT DEFAULT DATA
-- =============================================================================

-- Insert default categories
INSERT INTO categories (name, slug, description) VALUES
('Electronics', 'electronics', 'Electronic devices and accessories'),
('Clothing', 'clothing', 'Fashion and apparel'),
('Home & Garden', 'home-garden', 'Home improvement and gardening'),
('Books', 'books', 'Books and literature'),
('Sports & Outdoors', 'sports-outdoors', 'Sports equipment and outdoor gear'),
('Health & Beauty', 'health-beauty', 'Health and beauty products'),
('Toys & Games', 'toys-games', 'Toys and gaming products'),
('Automotive', 'automotive', 'Car parts and accessories');

-- Insert subcategories
INSERT INTO categories (name, slug, description, parent_id) VALUES
('Smartphones', 'smartphones', 'Mobile phones and accessories', 1),
('Laptops', 'laptops', 'Laptop computers', 1),
('Tablets', 'tablets', 'Tablet computers', 1),
('Men''s Clothing', 'mens-clothing', 'Clothing for men', 2),
('Women''s Clothing', 'womens-clothing', 'Clothing for women', 2),
('Shoes', 'shoes', 'Footwear for all', 2);

-- Insert default brands
INSERT INTO brands (name, slug, description) VALUES
('Apple', 'apple', 'Technology and electronics'),
('Samsung', 'samsung', 'Electronics and appliances'),
('Nike', 'nike', 'Sports and lifestyle brand'),
('Adidas', 'adidas', 'Sports and lifestyle brand'),
('Levi''s', 'levis', 'Denim and casual wear');

-- Insert default shipping zones
INSERT INTO shipping_zones (name, countries) VALUES
('Domestic', '["US"]'),
('International', '["CA", "MX", "GB", "AU", "DE", "FR"]');

-- Insert default shipping methods
INSERT INTO shipping_methods (zone_id, name, description, type, cost, estimated_days) VALUES
(1, 'Standard Shipping', 'Standard shipping within the US', 'flat_rate', 5.99, '3-5 business days'),
(1, 'Express Shipping', 'Express shipping within the US', 'flat_rate', 12.99, '1-2 business days'),
(1, 'Free Shipping', 'Free shipping for orders over $50', 'free_shipping', 0.00, '5-7 business days'),
(2, 'International Standard', 'Standard international shipping', 'flat_rate', 15.99, '7-14 business days'),
(2, 'International Express', 'Express international shipping', 'flat_rate', 29.99, '3-5 business days');

-- Insert default site settings
INSERT INTO site_settings (setting_key, setting_value, setting_type, description, is_public) VALUES
('site_name', 'Dione Ecommerce', 'text', 'Website name', TRUE),
('site_description', 'Modern ecommerce platform', 'text', 'Website description', TRUE),
('site_logo', '', 'text', 'Website logo URL', TRUE),
('site_favicon', '', 'text', 'Website favicon URL', TRUE),
('default_currency', 'USD', 'text', 'Default currency code', TRUE),
('currency_symbol', '$', 'text', 'Currency symbol', TRUE),
('tax_rate', '0.08', 'number', 'Default tax rate', FALSE),
('free_shipping_threshold', '50.00', 'number', 'Free shipping threshold amount', TRUE),
('maintenance_mode', 'false', 'boolean', 'Maintenance mode status', FALSE),
('user_registration_enabled', 'true', 'boolean', 'Allow user registration', TRUE),
('guest_checkout_enabled', 'true', 'boolean', 'Allow guest checkout', TRUE),
('email_verification_required', 'false', 'boolean', 'Require email verification', FALSE),
('max_file_upload_size', '10485760', 'number', 'Maximum file upload size in bytes', FALSE),
('products_per_page', '12', 'number', 'Products per page in listing', TRUE),
('enable_product_reviews', 'true', 'boolean', 'Enable product reviews', TRUE),
('auto_approve_reviews', 'false', 'boolean', 'Auto approve product reviews', FALSE),
('smtp_host', '', 'text', 'SMTP server host', FALSE),
('smtp_port', '587', 'number', 'SMTP server port', FALSE),
('smtp_username', '', 'text', 'SMTP username', FALSE),
('smtp_password', '', 'text', 'SMTP password', FALSE),
('smtp_encryption', 'tls', 'text', 'SMTP encryption type', FALSE),
('payment_gateway', 'stripe', 'text', 'Default payment gateway', FALSE),
('stripe_public_key', '', 'text', 'Stripe public key', FALSE),
('stripe_secret_key', '', 'text', 'Stripe secret key', FALSE),
('paypal_client_id', '', 'text', 'PayPal client ID', FALSE),
('paypal_client_secret', '', 'text', 'PayPal client secret', FALSE),
('google_analytics_id', '', 'text', 'Google Analytics tracking ID', FALSE),
('facebook_pixel_id', '', 'text', 'Facebook Pixel ID', FALSE);

-- Insert default admin user (password should be hashed in production)
INSERT INTO users (email, password, username, role, is_approved, email_verified) VALUES
('admin@dione.com', 'pbkdf2:sha256:260000$salt$hash_here', 'admin', 'admin', TRUE, TRUE);

-- =============================================================================
-- CREATE ADDITIONAL INDEXES FOR PERFORMANCE
-- =============================================================================

-- User table indexes
CREATE INDEX idx_user_last_login ON users(last_login);
CREATE INDEX idx_user_email_verified ON users(email_verified);

-- Product table indexes
CREATE INDEX idx_product_featured_active ON products(featured, status);
CREATE INDEX idx_product_price_range ON products(price, status);
CREATE INDEX idx_product_stock_status ON products(stock_status);
CREATE INDEX idx_product_seller_status ON products(seller_id, status);

-- Order table indexes
CREATE INDEX idx_order_date_status ON orders(created_at, status);
CREATE INDEX idx_order_amount ON orders(total_amount);
CREATE INDEX idx_order_customer_date ON orders(user_id, created_at);

-- Performance indexes for analytics
CREATE INDEX idx_product_view_date ON product_views(created_at);
CREATE INDEX idx_search_date ON search_queries(created_at);

-- =============================================================================
-- TRIGGERS FOR AUTOMATED TASKS
-- =============================================================================

-- Update product stock when order items are created
DELIMITER //
CREATE TRIGGER update_product_stock_on_order
    AFTER INSERT ON order_items
    FOR EACH ROW
BEGIN
    -- Update product total stock
    UPDATE products 
    SET total_stock = total_stock - NEW.quantity,
        total_sold = total_sold + NEW.quantity
    WHERE id = NEW.product_id;
    
    -- Update variant stock if variant is specified
    IF NEW.variant_id IS NOT NULL THEN
        UPDATE product_stocks ps
        JOIN product_variants pv ON ps.variant_id = pv.id
        SET ps.stock_quantity = ps.stock_quantity - NEW.quantity
        WHERE pv.id = NEW.variant_id;
    END IF;
END//

-- Update product rating when review is added/updated
CREATE TRIGGER update_product_rating
    AFTER INSERT ON reviews
    FOR EACH ROW
BEGIN
    UPDATE products p
    SET rating = (
        SELECT AVG(r.rating)
        FROM reviews r
        WHERE r.product_id = NEW.product_id AND r.is_approved = TRUE
    ),
    review_count = (
        SELECT COUNT(*)
        FROM reviews r
        WHERE r.product_id = NEW.product_id AND r.is_approved = TRUE
    )
    WHERE p.id = NEW.product_id;
END//

-- Update seller statistics
CREATE TRIGGER update_seller_stats
    AFTER UPDATE ON orders
    FOR EACH ROW
BEGIN
    IF NEW.status = 'delivered' AND OLD.status != 'delivered' THEN
        UPDATE sellers s
        SET total_sales = (
            SELECT COALESCE(SUM(oi.total), 0)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE oi.seller_id = s.id AND o.status = 'delivered'
        ),
        total_orders = (
            SELECT COUNT(DISTINCT oi.order_id)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE oi.seller_id = s.id AND o.status = 'delivered'
        )
        WHERE s.id IN (
            SELECT DISTINCT oi.seller_id
            FROM order_items oi
            WHERE oi.order_id = NEW.id
        );
    END IF;
END//

DELIMITER ;

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Product listing view with seller info
CREATE VIEW product_listings AS
SELECT 
    p.id,
    p.name,
    p.slug,
    p.description,
    p.price,
    p.compare_at_price,
    p.image,
    p.rating,
    p.review_count,
    p.total_stock,
    p.status,
    p.featured,
    p.created_at,
    s.business_name as seller_name,
    s.rating as seller_rating,
    c.name as category_name,
    c.slug as category_slug,
    b.name as brand_name
FROM products p
LEFT JOIN sellers s ON p.seller_id = s.id
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN brands b ON p.brand_id = b.id
WHERE p.status = 'active';

-- Order summary view
CREATE VIEW order_summaries AS
SELECT 
    o.id,
    o.order_number,
    o.status,
    o.payment_status,
    o.total_amount,
    o.created_at,
    o.updated_at,
    CONCAT(o.billing_first_name, ' ', o.billing_last_name) as customer_name,
    o.billing_email as customer_email,
    COUNT(oi.id) as item_count,
    GROUP_CONCAT(CONCAT(oi.product_name, ' (', oi.quantity, ')') SEPARATOR ', ') as items_summary
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id;

-- Seller dashboard view
CREATE VIEW seller_dashboard AS
SELECT 
    s.id as seller_id,
    s.business_name,
    COUNT(DISTINCT p.id) as total_products,
    COUNT(DISTINCT CASE WHEN p.status = 'active' THEN p.id END) as active_products,
    SUM(p.total_stock) as total_inventory,
    AVG(p.rating) as avg_product_rating,
    s.total_sales,
    s.total_orders,
    s.rating as seller_rating
FROM sellers s
LEFT JOIN products p ON s.id = p.seller_id
GROUP BY s.id;

COMMIT;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================