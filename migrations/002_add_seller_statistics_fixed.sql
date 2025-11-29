-- Migration: Add seller statistics tracking (Fixed)
-- This migration adds fields to track seller statistics for the product dropdown details

-- Add statistics columns to seller table (not seller_profiles)
ALTER TABLE seller ADD COLUMN IF NOT EXISTS rating_count INTEGER DEFAULT 0;
ALTER TABLE seller ADD COLUMN IF NOT EXISTS products_count INTEGER DEFAULT 0;
ALTER TABLE seller ADD COLUMN IF NOT EXISTS followers_count INTEGER DEFAULT 0;
ALTER TABLE seller ADD COLUMN IF NOT EXISTS total_sales INTEGER DEFAULT 0;
ALTER TABLE seller ADD COLUMN IF NOT EXISTS last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update existing sellers with default values
UPDATE seller SET 
    rating_count = 0,
    products_count = 0, 
    followers_count = 0,
    total_sales = 0,
    last_active = CURRENT_TIMESTAMP
WHERE rating_count IS NULL OR products_count IS NULL OR followers_count IS NULL;