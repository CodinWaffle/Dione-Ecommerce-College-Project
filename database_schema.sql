-- Dione Ecommerce Database Schema
-- Complete SQL schema for the entire project

-- Create database
CREATE DATABASE IF NOT EXISTS dione_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dione_data;

-- User table (main users table)
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255),
    username VARCHAR(150),
    role VARCHAR(20) NOT NULL DEFAULT 'buyer',
    role_requested VARCHAR(20),
    is_approved BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
);

-- OAuth table for social authentication
CREATE TABLE oauth (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    token TEXT,
    provider_user_id VARCHAR(256) NOT NULL,
    provider_user_login VARCHAR(256),
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE KEY unique_provider_user (provider, provider_user_id),
    INDEX idx_oauth_user_id (user_id)
);

-- Buyer profile table
CREATE TABLE buyer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    zip_code VARCHAR(20),
    country VARCHAR(100),
    preferred_language VARCHAR(50) DEFAULT 'English',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_buyer_user_id (user_id)
);

-- Seller profile table
CREATE TABLE seller (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100),
    business_address TEXT,
    business_city VARCHAR(100),
    business_zip VARCHAR(20),
    business_country VARCHAR(100),
    bank_type VARCHAR(50),
    bank_name VARCHAR(255),
    bank_account VARCHAR(100),
    bank_holder_name VARCHAR(255),
    tax_id VARCHAR(50),
    store_description TEXT,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_seller_user_id (user_id),
    INDEX idx_seller_verified (is_verified)
);

-- Rider profile table
CREATE TABLE rider (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    license_number VARCHAR(50),
    vehicle_type VARCHAR(50),
    vehicle_number VARCHAR(50),
    availability_status VARCHAR(20) DEFAULT 'available',
    current_location VARCHAR(255),
    delivery_zones TEXT,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_date DATETIME,
    rating FLOAT DEFAULT 0.0,
    total_deliveries INT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_rider_user_id (user_id),
    INDEX idx_rider_status (availability_status),
    INDEX idx_rider_verified (is_verified)
);

-- Site settings table
CREATE TABLE site_setting (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(64) NOT NULL UNIQUE,
    value TEXT NOT NULL DEFAULT '',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_site_setting_key (`key`)
);

-- Product table (main products)
CREATE TABLE product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    price DECIMAL(10,2) NOT NULL DEFAULT 0,
    compare_at_price DECIMAL(10,2),
    stock INT NOT NULL DEFAULT 0,
    sku VARCHAR(100),
    barcode VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    discount_type VARCHAR(20),
    discount_value DECIMAL(6,2),
    voucher_type VARCHAR(50),
    materials TEXT,
    details_fit TEXT,
    model_height VARCHAR(50),
    wearing_size VARCHAR(50),
    allow_backorder BOOLEAN DEFAULT FALSE,
    track_inventory BOOLEAN DEFAULT TRUE,
    low_stock_threshold INT DEFAULT 0,
    attributes JSON,
    image VARCHAR(512),
    secondary_image VARCHAR(512),
    tags TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_product_seller_id (seller_id),
    INDEX idx_product_category (category),
    INDEX idx_product_status (status),
    INDEX idx_product_created_at (created_at)
);

-- Seller product management table (enhanced product management)
CREATE TABLE seller_product_management (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    compare_at_price DECIMAL(10,2),
    discount_type VARCHAR(50),
    discount_value DECIMAL(10,2),
    voucher_type VARCHAR(50),
    materials TEXT,
    details_fit TEXT,
    primary_image VARCHAR(500),
    secondary_image VARCHAR(500),
    total_stock INT DEFAULT 0,
    low_stock_threshold INT DEFAULT 5,
    variants JSON,
    attributes JSON,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_seller_product_seller_id (seller_id),
    INDEX idx_seller_product_category (category),
    INDEX idx_seller_product_created_at (created_at)
);

-- Warning table (admin warnings to users)
CREATE TABLE warning (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    admin_id INT,
    template_key VARCHAR(100),
    subject VARCHAR(255),
    body TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES user(id) ON DELETE SET NULL,
    INDEX idx_warning_user_id (user_id),
    INDEX idx_warning_admin_id (admin_id),
    INDEX idx_warning_created_at (created_at)
);

-- Chat messages table (user-admin communication)
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    admin_id INT,
    sender_name VARCHAR(255),
    sender_role VARCHAR(50),
    body TEXT NOT NULL,
    attachment VARCHAR(512),
    is_from_admin BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES user(id) ON DELETE SET NULL,
    INDEX idx_chat_user_id (user_id),
    INDEX idx_chat_admin_id (admin_id),
    INDEX idx_chat_is_read (is_read),
    INDEX idx_chat_created_at (created_at)
);

-- Product reports table (product flagging system)
CREATE TABLE product_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    reporter_id INT,
    reason VARCHAR(100) NOT NULL,
    details TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES user(id) ON DELETE SET NULL,
    INDEX idx_product_reports_product_id (product_id),
    INDEX idx_product_reports_reporter_id (reporter_id),
    INDEX idx_product_reports_resolved (resolved),
    INDEX idx_product_reports_created_at (created_at)
);

-- Insert default site settings
INSERT INTO site_setting (`key`, value) VALUES
('site_name', 'Dione Ecommerce'),
('site_description', 'Modern ecommerce platform'),
('maintenance_mode', 'false'),
('registration_enabled', 'true'),
('email_verification_required', 'false'),
('max_file_upload_size', '10485760'),
('default_currency', 'USD'),
('tax_rate', '0.00'),
('shipping_enabled', 'true'),
('guest_checkout_enabled', 'true');

-- Insert default admin user (password should be hashed in production)
INSERT INTO user (email, password, username, role, is_approved) VALUES
('admin@dione.com', 'pbkdf2:sha256:260000$salt$hash', 'admin', 'admin', TRUE);

-- Create indexes for better performance
CREATE INDEX idx_user_created_at ON user(created_at);
CREATE INDEX idx_product_price ON product(price);
CREATE INDEX idx_product_stock ON product(stock);
CREATE INDEX idx_seller_product_price ON seller_product_management(price);
CREATE INDEX idx_seller_product_stock ON seller_product_management(total_stock);

-- Create full-text search indexes for product search
ALTER TABLE product ADD FULLTEXT(name, description, tags);
ALTER TABLE seller_product_management ADD FULLTEXT(name, description);

COMMIT;