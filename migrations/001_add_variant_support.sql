-- Migration: Add support for multiple sizes per variant
-- Up migration

-- Create product_variants table
CREATE TABLE IF NOT EXISTS product_variants (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    variant_name VARCHAR(255) NOT NULL,
    variant_sku VARCHAR(255),
    images_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_variants_product_id (product_id),
    FOREIGN KEY (product_id) REFERENCES seller_product_management(id) ON DELETE CASCADE
);

-- Create variant_sizes table
CREATE TABLE IF NOT EXISTS variant_sizes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    variant_id BIGINT NOT NULL,
    size_label VARCHAR(50) NOT NULL,
    stock_quantity INT DEFAULT 0,
    sku VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_variant_sizes_variant_id (variant_id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE CASCADE
);

-- Create product_descriptions table
CREATE TABLE IF NOT EXISTS product_descriptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    description_text TEXT,
    materials TEXT,
    care_instructions TEXT,
    details_fit TEXT,
    meta_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_descriptions_product_id (product_id),
    FOREIGN KEY (product_id) REFERENCES seller_product_management(id) ON DELETE CASCADE
);

-- Add status column to seller_product_management if it doesn't exist
ALTER TABLE seller_product_management 
ADD COLUMN IF NOT EXISTS base_sku VARCHAR(255),
ADD COLUMN IF NOT EXISTS draft_data JSON,
ADD COLUMN IF NOT EXISTS is_draft BOOLEAN DEFAULT TRUE;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_seller_product_status ON seller_product_management(status);
CREATE INDEX IF NOT EXISTS idx_seller_product_draft ON seller_product_management(is_draft);

COMMIT;